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

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

from functions.get_files_info import schema_get_files_info

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

def main():
    try:
        if len(sys.argv) < 2:
            print("No input provided. Exiting.")
            sys.exit(1)
            
        user_prompt = sys.argv[1]
        
        messages = [
            types.Content(role="user", parts=[types.Part(text=user_prompt)]),
        ]
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-001", 
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt)
        )
        
        if "--verbose" in sys.argv:
            print(f"User prompt: {response.text}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        elif response.function_calls:
            for function_call_part in response.function_calls:
                print(f"Calling function: {function_call_part.name}({function_call_part.args})")
        else:
            print(response.text)
            
    except IndexError:
        print("No input provided. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()


