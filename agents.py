import os
import io
import contextlib
from crewai import Agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Set up the API key for Groq
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the Groq model
llm = ChatGroq(
    api_key=groq_api_key,
    model="mixtral-8x7b-32768"
)

class PythonExecutorAgent(Agent):
    def execute(self, code, file_name):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            try:
                exec(code)
                return output.getvalue(), None
            except Exception as e:
                return output.getvalue(), str(e)

# Define agents
executor_agent = PythonExecutorAgent(
    role="Python Executor",
    goal="Execute the given Python code and capture the output or any errors.",
    backstory=(
        "You are a Python executor agent designed to run code and capture the output or any errors. "
        "You will execute the provided code and return the output or any exceptions that occur during execution."
    ),
    allow_delegation=False,
    verbose=True
)

analyzer = Agent(
    role="Code Analyzer",
    goal="Thoroughly analyze the provided Python code to identify any syntactical, logical, or runtime errors. Provide a detailed report outlining the issues and potential causes.",
    backstory=(
        "You are a seasoned Python developer with years of experience in identifying and debugging code issues. "
        "Your expertise spans across various domains, making you well-versed in pinpointing subtle and complex errors. "
        "Your task is to meticulously analyze the given code, identify any issues, and provide a comprehensive report that includes "
        "the nature of the errors, their potential causes, and suggestions for improvements. Your analysis will serve as the foundation "
        "for subsequent agents to correct and refine the code."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

fixer = Agent(
    role="Bug Fixer",
    goal="Take the analysis report and fix all identified bugs in the given Python code. Ensure the code is correct, efficient, and follows best practices.",
    backstory=(
        "You are an experienced Python developer known for your ability to quickly and effectively fix bugs. "
        "Your role is to take the detailed analysis report and address each identified issue. You will correct syntax errors, fix logical mistakes, "
        "and resolve runtime issues. Your fixes should be accompanied by comments explaining the changes made, "
        "ensuring clarity and transparency. The corrected code will then be passed on for further review."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

reviewer = Agent(
    role="Code Reviewer",
    goal="Review the fixed Python code to ensure it meets best practices for readability, efficiency, and correctness. Provide feedback or further corrections if necessary.",
    backstory=(
        "You are a Python expert with a keen eye for detail and best practices. Your job is to review the fixed code, ensuring it adheres to high standards of quality and performance. "
        "You will evaluate the code for readability, logical correctness, efficiency, and adherence to best practices. If any issues remain, you will provide constructive feedback and "
        "recommendations for further improvements. Your review will ensure the code is polished and ready for execution."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

runner = Agent(
    role="Code Runner",
    goal="Execute the provided Python code and report any runtime errors or unexpected behavior. Ensure that the code produces the expected output.",
    backstory=(
        "You are an automation expert responsible for running the code and verifying its execution. "
        "Your role is to ensure that the code runs correctly and produces the intended results without any issues. "
        "You will execute the code, monitor its behavior, and report any runtime errors or unexpected outcomes. "
        "If the code does not perform as expected, your feedback will guide further refinements."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)