import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv('.env')

# OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')

# Bug description to check against
bug_description = """
Bug -
Title - Resolve Loader Exception for valid pdf files.
Description - When I uploaded a valid file, loader process throws  exception with the message that can't read an empty file.
Actual Behaviour : The file should be processed as it is not an empty file and the chatbox should appear without throwing any exception.
"""

# Directory path to analyze
directory_path = 'chatbotui-master'

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Function to get all .py files in a directory and subdirectories
def get_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

# Get all .py files in the directory
python_files = get_python_files(directory_path)

# Analyze each .py file
for file_path in python_files:
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Prepare messages for OpenAI Chat Completions API
    messages = [
        {"role": "system", "content": "You are the developer and you have to fix the bug in code. But before that, you are given the bug description and a python file content. Please analyze and find out if that bug can be in this file. Respond with only a `No` if the bug (related to the bug description) is not in the file and `Yes` if bug (related to the bug description) is there in the file."},
        {"role": "user", "content": bug_description},
        {"role": "user", "content": f"Here is the content of the file {file_path}:\n\n{file_content}"}
    ]

    # Call OpenAI Chat Completions API
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages
    )

    # Print the response from the API in the desired format
    analysis_result = response.choices[0].message.content
    print(f"I am analyzing {file_path}:\n{analysis_result}\n")