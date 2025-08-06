import os
from functions.config import MAX_CHARS

from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read the contents of a specific file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read",
            ),
        },
        required=["file_path"]
    )
)

def get_file_content(file_path, working_directory="./calculator"):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" is not a file'
    
    try:
        with open(target_file, "r") as file:
            content = file.read(MAX_CHARS + 1)
            if len(content) > MAX_CHARS:
                return f"Error: File '{file_path}' truncated at {MAX_CHARS} characters"
            return content
    except Exception as e:
        return f"Error: {e}"