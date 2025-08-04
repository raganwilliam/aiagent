import os
from functions.config import MAX_CHARS

def get_file_content(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" is not a file'
    
    try:
        with open(target_file, "r") as file:
            content = file.read(MAX_CHARS)
            if len(content) <= MAX_CHARS:
                return content
            if len(content) > MAX_CHARS:
                return f"Error: File '{file_path}' truncated at {MAX_CHARS} characters"
    except Exception as e:
        return f"Error: {e}"