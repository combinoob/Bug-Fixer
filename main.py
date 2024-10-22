import os
from agents import executor_agent, analyzer, fixer, reviewer, runner
from tasks import CodeTasks
from crewai import Crew
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load all Python files in the 'codebase' directory recursively
codebase_dir = 'chatbotui-master'
python_files = []
for root, dirs, files in os.walk(codebase_dir):
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))

# Read content of all Python files
code_files = {file: open(file, 'r').read() for file in python_files}

human_instruction = """
Title - Resolve Loader Exception for valid pdf files.
Description - When I uploaded a valid file, loader process throws exception with the message that can't read an empty file.
Actual Behaviour: The file should be processed as it is not an empty file and the chatbox should appear without throwing any exception.
Problem statement - Generate the fix for the above bug (issue).
Predicted fix - Your agent should give the fix for the above bug/issue
"""
previous_result = ""

# Initialize tasks
tasks = CodeTasks()

# Store results
fixed_files = {}

# Process each file
for file, code in code_files.items():
    execute_task = tasks.execute_code(agent=executor_agent, code=code, file_name=file)
    analyze_task = tasks.analyze_code(agent=analyzer, code=code, human_instruction=human_instruction, previous_result="{output_of_execute_task}", file_name=file)
    fix_task = tasks.fix_code(agent=fixer, analysis="{output_of_analyze_task}", file_name=file)
    review_task = tasks.review_code(agent=reviewer, fixed_code="{output_of_fix_task}", file_name=file)
    run_task = tasks.run_code(agent=runner, code="{output_of_review_task}", file_name=file)

    crew = Crew(
        agents=[executor_agent, analyzer, fixer, reviewer, runner],
        tasks=[execute_task, analyze_task, fix_task, review_task, run_task],
        verbose=2
    )

    result = crew.kickoff()
    previous_result = "{output_of_run_task}"

    # Assume the result contains information on whether the file was fixed
    if "fixed_code" in result:
        fixed_files[file] = result["fixed_code"]

# Print the files that were fixed along with their corrected code
print("The following files were fixed:")
for file, fixed_code in fixed_files.items():
    print(f"Filename: {file}")
    print("Corrected code:")
    print(fixed_code)
    print("\n" + "-"*80 + "\n")

print("All files processed.")