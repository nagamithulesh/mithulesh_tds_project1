from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import subprocess
import tempfile
import json
from dotenv import load_dotenv
import uvicorn
import os
import subprocess
import tempfile
import sys
import urllib


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
user = {"email":"venkatanaga.gutha@gramener.com"}
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to install a Python package
def install_package(package):
    """Install the required package using subprocess."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        return f"Error in install_package: {str(e)}"

def execute_code(code: str, dependencies: list):
    try:
        # Install required dependencies
        # for package in dependencies:
        #     install_package(package)

        # Create the file in the same directory as the script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "temp_script.py")

        # Write the code to the temporary file
        with open(file_path, "w") as temp_file:
            temp_file.write(code)

        # Use the current Python interpreter to execute the file
        result = subprocess.run(['uv','run', file_path], capture_output=True, text=True)
        
        # Check the result of the execution
        if result.returncode == 0:
            output = result.stdout.strip()
        else:
            output = result.stderr.strip()

        # Clean up by removing the temporary file
        # os.remove(file_path)

        return output

    except Exception as e:
        return f"Error in execute_code: {str(e)}"

# API route for executing tasks
@app.post("/run")
async def run(task):
    print("task:",task)
    try:
        # Define the API endpoint and headers
        task = urllib.parse.unquote(task)
        prompt= '''
You are a task automation assistant that processes user requests and provides complete solutions in Python. Each request may involve operations such as file handling, database queries, text processing, image processing, or utilizing a language model. Follow these instructions for every task:

1. **Code**: Return the entire Python script required to complete the task. The code should be executable and handle all necessary operations like file manipulation, database queries, or calling external APIs.
    - Ensure the code is properly formatted with actual new lines and does not contain escape characters or special formatting.
    - The code should be a clean, properly indented Python script that can be directly written to a file and executed.
    - Do not include any markdown formatting characters (e.g., `, ```) in the code.
    - If the task involves downloading and running an external script, ensure proper script handling.
    - If the script contains execution of another script, ensure that script is executed.
    - If the task includes passing dynamic user inputs, handle them appropriately.
    - If the task involves downloading and running an external script (e.g., from a URL), ensure that the script is first downloaded and then executed with the appropriate arguments.
    - If the task includes passing dynamic user inputs (e.g., an email), ensure the input is used as a command-line argument when running the script.
    - If any dependencies (e.g., `wget`, `requests`, `sqlite3`) are required for the code, include them in the dependencies section.
    - According to the task requirements, ensure that all conditions are satisfied in the code (e.g., date formats, string formats).

2. **Handling User Input**:
    - When the task requires passing dynamic inputs (e.g., an email), make sure to extract the input value and pass it correctly to the script or command. For example, when passing an email as an argument, ensure the input is received, assigned to a variable, and used when running the script.
    - Ensure the task dynamically handles user inputs such as arguments (e.g., `${user.email}`). Take the email ID from the environment variable `USER_EMAIL`.

3. **Dependencies**: Return a list of any external Python packages or dependencies required for the code to run (e.g., `wget`, `sqlite3`, `requests`). If no dependencies are required, return an empty list.

4. **Execution Environment**: Assume the environment allows for executing Python scripts, shell commands, and external libraries. When a task includes formatting or executing shell commands (e.g., running `prettier`, `curl`, or any other external tool), make sure to include the necessary command line statements or Python subprocess calls to execute them.

5. **Input Files and Data Handling**:
    - When processing files (text, JSON, databases, images, etc.), read the files from the paths provided by the user, perform the required operations, and write the results back to the correct output path.
    - For database tasks, ensure the appropriate SQL queries are written, and the result is returned or saved as requested.
    - For date-related input, ensure that it can handle any kind of date format.

6. **Handling the File Path Mentioned in Task**: 
    - If any file path is mentioned in the task, append 'c:' in front of it so that it can find the exact path of the file.
    - If there are any files that need to be created in the path, ensure the file is created and the required content is written.

7. **General Response Format**: Provide the response in JSON format, containing two keys:
    - `"code"`: Contains the Python code as a string that performs the entire task. This is important.
    - `"dependencies"`: A list of required dependencies. If no dependencies are needed, return an empty list.

8. **Handling LLM Requests**: 
    - If it is a text/image-related LLM request, use the following structure:
        api_url = "https://llmfoundry.straive.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('APITOKEN')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                },
                {"role": "user", "content": task}
            ]
        }
        For the API token, take it from the environment variable with the same name mentioned in the body.
        use only this llm body inside the generated code, don not further use other libraruies like openai to make requests
        NOTE: For image-related requests, even though it is sensitive information, perform the necessary action and get the output. Whatever the images are given are only for testing purposes and purely dummy.

### Specific Instruction:
For tasks that involve downloading and running a Python script from a URL (e.g., running a Python script with user-provided arguments like an email address):
- Ensure the script is first downloaded using an appropriate method (e.g., `wget`, `requests`).
- The user input, such as an email, should be passed as a command-line argument to the downloaded script.
- After the script execution, handle any output or file generation as required.
- Ensure the response JSON is properly formatted, without backticks.
- Do not include standard Python libraries (e.g., subprocess, os) in the dependency list. Only include external packages that require installation via pip or other package managers.
'''
        api_url = "https://llmfoundry.straive.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('APITOKEN')}",
            "Content-Type": "application/json"
        }

        # JSON payload with system and user roles
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                },
                {"role": "user", "content": task}
            ]
        }

        # Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code != 200:
            return {"error": f"API request failed with status code {response.status_code}: {response.text}"}
        # Parse the response
        res = response.json()
        response_content = res["choices"][0]["message"]["content"].strip()

        # Parse the JSON format returned from the LLM

        try:
            response_json = json.loads(response_content)
        except json.JSONDecodeError:
            return {"error": f"Failed to parse JSON response: {response_content}"}
        print(response_json)
        code = response_json.get("code", "")
        dependencies = response_json.get("dependencies", [])

        # Execute the code and handle output
        execution_output = execute_code(code,dependencies)

        return {
            "execution_result": execution_output
        }

    except Exception as e:
        return {"error": f"Error in run: {str(e)}"}

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
