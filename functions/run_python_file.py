import os
import subprocess

def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(target_file):
        return f'Error: File "{file_path}" not found.'
    
    if not target_file.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file'
    try:
        completed_process = subprocess.run(
            ['python3', target_file] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=abs_working_dir,
            timeout=30,
            text=True
        )
        output = []
        if completed_process.stdout:
            output.append(f"STDOUT: {completed_process.stdout}")
        if completed_process.stderr:
            output.append(f"STDERR: {completed_process.stderr}")
        if completed_process.returncode != 0:
            output.append(f"Process exited with code {completed_process.returncode}")
        if not output:
            return "No output produced."
        return "\n".join(output)
    except Exception as e:
        return f"Error running file: {e}"
    

