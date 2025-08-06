import sys

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai

client = genai.Client(api_key=api_key)

from google.genai import types

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories using get_files_info
- Read file contents using get_file_content  
- Execute Python files using run_python_file (use this when users say "run", "execute", or "test" a .py file)
- Write or overwrite files using write_file

When users ask to "run" or "execute" a Python file, always use the run_python_file function.

All paths you provide should be relative to the working directory which is defined in the function calls.
Please iteratively search for file names and directories --these may be listed as nouns-- in the working directory, and return results in a user-friendly format.
If you encounter any errors, return them in a user-friendly format.
"""

from functions.get_files_info import *
from functions.get_file_content import *
from functions.run_python_file import *
from functions.write_file import *

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file, 
        schema_write_file,
    ]
)

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = function_call_part.args

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    # Add working_directory to all function calls
    args["working_directory"] = "./calculator"

    if function_name == "get_files_info":
        function_result = get_files_info(**args)
    elif function_name == "get_file_content":
        function_result = get_file_content(**args)
    elif function_name == "run_python_file":
        function_result = run_python_file(**args)
    elif function_name == "write_file":
        function_result = write_file(**args)
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


def main():
    try:
        if len(sys.argv) < 2:
            print("No input provided. Exiting.")
            sys.exit(1)
            
        user_prompt = sys.argv[1]
        verbose = "--verbose" in sys.argv
        
        messages = [
            types.Content(role="user", parts=[types.Part(text=user_prompt)]),
        ]
        
        max_iterations = 20
        for iteration in range(max_iterations):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash-001", 
                    contents=messages,
                    config=types.GenerateContentConfig(
                        tools=[available_functions], system_instruction=system_prompt)
                )
            except Exception as e:
                print(f"Fatal error during model call: {str(e)}")
                sys.exit(1)

            # Add all candidate contents to messages (if any)
            if hasattr(response, "candidates"):
                for candidate in response.candidates:
                    if hasattr(candidate, "content"):
                        messages.append(candidate.content)

            # Handle function calls
            if response.function_calls:
                for function_call_part in response.function_calls:
                    function_call_result = call_function(function_call_part, verbose=verbose)
                    try:
                        function_response = function_call_result.parts[0].function_response.response
                    except (AttributeError, IndexError):
                        raise RuntimeError("Fatal: Function call did not return a valid response object.")
                    # Add the function response to messages as a tool message
                    tool_message = types.Content(
                        role="tool",
                        parts=[types.Part.from_function_response(
                            name=function_call_part.name,
                            response=function_response
                        )]
                    )
                    messages.append(tool_message)
                    if verbose:
                        print(f"-> {function_response}")
                    #else:
                    #    print(function_response)
                # Continue to next iteration for further model steps
                continue
            else:
                # Only print response.text if there are no function calls
                if hasattr(response, "text") and response.text:
                    print(response.text)
                else:
                    print("No function calls and no final response. Exiting.")
                break
        else:
            print("Max iterations reached. Exiting.")
            
    except IndexError:
        print("No input provided. Exiting.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()


