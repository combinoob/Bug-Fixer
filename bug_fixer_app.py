import os
import zipfile
import json
from io import BytesIO
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import ast

# Load environment variables
load_dotenv('.env')

# OpenAI API key from environment variable
api_key = os.getenv('GROQ_API_KEY')

# Initialize OpenAI client
client = Groq(api_key=api_key)

# Function to analyze a single file for the presence of a bug
def analyze_file(file_path, file_content, bug_description, file_dependencies):
    # Prepare messages for OpenAI Chat Completions API
    dependencies = file_dependencies.get(file_path, [])
    dependencies_text = f"The file {file_path} imports the following files: {', '.join(dependencies)}"
    messages = [
        {"role": "system", "content": "You are the developer and you have to fix the bug in code. But before that, you are given the bug description, the file content, and its dependencies. Please analyze and find out if the bug, that is related to the bug description, can be in this file. Respond with only a `Yes` if the bug (given in the bug description) is there in the file and the file requires a fix, otherwise respond with only a `No`."},
        {"role": "user", "content": bug_description},
        {"role": "user", "content": dependencies_text},
        {"role": "user", "content": f"Here is the content of the file {file_path}:\n\n{file_content}"}
    ]

    # Call OpenAI Chat Completions API
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=messages
    )

    # Get the response from the API
    analysis_result = response.choices[0].message.content.strip()
    return analysis_result

# Function to get the fixed code from OpenAI
def get_fixed_code(file_path, file_content, bug_description, file_dependencies):
    # Prepare messages for OpenAI Chat Completions API
    dependencies = file_dependencies.get(file_path, [])
    dependencies_text = f"The file {file_path} imports the following files: {', '.join(dependencies)}"
    messages = [
        {"role": "system", "content": "You are an expert developer tasked with fixing the bug in the given code. Here is the bug description, the file content, and its dependencies. Please provide the fixed code along with an explanation."},
        {"role": "user", "content": bug_description},
        {"role": "user", "content": dependencies_text},
        {"role": "user", "content": f"Here is the content of the file {file_path}:\n\n{file_content}"}
    ]

    # Call OpenAI Chat Completions API
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=messages
    )

    # Get the response from the API
    return response.choices[0].message.content.strip()

# Function to get imports from a Python file
def get_imports(filepath):
    with open(filepath, 'r') as file:
        tree = ast.parse(file.read(), filename=filepath)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    return imports

# Function to find all Python files in a directory
def find_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

# Function to check if an import is a project import
def is_project_import(import_name, project_directory, python_files):
    project_files = {os.path.splitext(os.path.relpath(file, project_directory))[0].replace(os.path.sep, '.') for file in python_files}
    return import_name in project_files

# Function to get project imports for a file
def get_project_imports(filepath, project_directory, python_files):
    imports = get_imports(filepath)
    project_imports = [imp for imp in imports if is_project_import(imp, project_directory, python_files)]
    return project_imports

# Function to build dependency dictionary
def build_dependency_dict(python_files, project_directory):
    dependency_dict = {}
    for file in python_files:
        try:
            file_imports = get_project_imports(file, project_directory, python_files)
            dependency_dict[file] = [os.path.join(project_directory, imp.replace('.', os.path.sep) + '.py') for imp in file_imports]
        except:
            pass
    return dependency_dict

# Streamlit UI
st.title("Bug Fixer for Repository")

# Text area for entering bug description
bug_description = st.text_area("Enter the Bug Description", value=""" """)

# Upload ZIP file
zip_file = st.file_uploader("Upload repository ZIP file", type="zip")

if st.button('Analyze and Fix') and zip_file:
    # Read the uploaded ZIP file
    zip_bytes = BytesIO(zip_file.read())

    # Open the ZIP file in memory
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        # Extract the ZIP file to a temporary directory
        temp_dir = "temp_repo"
        zip_ref.extractall(temp_dir)

        # Find all Python files in the extracted directory
        python_files = find_python_files(temp_dir)

        # Build the dependency dictionary
        file_dependencies = build_dependency_dict(python_files, temp_dir)

        # Dictionary to store analysis results
        analysis_results = {}

        # Iterate through each file in the ZIP
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.py'):
                with zip_ref.open(file_info) as file:
                    file_content = file.read().decode('utf-8')

                # Get the analysis result
                analysis_result = analyze_file(file_info.filename, file_content, bug_description, file_dependencies)

                # Store the result in the dictionary
                analysis_results[file_info.filename] = analysis_result

        # Display analysis results
        st.subheader("Probable Buggy Files:")
        buggy_files = [file_path for file_path, result in analysis_results.items() if result == 'Yes']
        for file_path in buggy_files:
            st.write(file_path)

        st.subheader("Fixed Code with Explanation:")

        # Iterate through the analysis results and fix the files with "Yes" result
        for file_path in buggy_files:
            with zip_ref.open(file_path) as file:
                file_content = file.read().decode('utf-8')

            # Get the fixed code from OpenAI
            fixed_code_response = get_fixed_code(file_path, file_content, bug_description, file_dependencies)

            # Display the file name and the fixed code response
            st.subheader(f"File: {file_path}")
            st.text_area("Fixed Code with Explanation:", value=fixed_code_response, height=300)

# Instructions
st.info("Please enter the bug description and upload the repository ZIP file to proceed. Click 'Analyze and Fix' to start the process.")