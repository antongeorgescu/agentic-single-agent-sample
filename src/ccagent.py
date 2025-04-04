import os
import asyncio
from typing import Any
from langchain_openai import AzureChatOpenAI
from langchain.agents import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich import print
from rich.markdown import Markdown

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import debugpy

import sys
sys.path.append('/src')

import logging
logging.getLogger('faker.factory').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)
# Suppress detailed "Thinking" messages
logging.getLogger('langchain.agent').setLevel(logging.WARNING)

from tools import apirequests, synthdata
from utils import logger

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="./.env")

llm = AzureChatOpenAI(
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
    max_retries = 3,
    verbose = True,
    # temperature=0.2,
    # max_tokens=2000  # Adjust this value as needed

)

# Define the tools: deliberatley eliminate some of them and use GenAI to fulfill the task  
tools = [
    apirequests.create_nonregistered_student, 
    apirequests.add_communication_info,
    apirequests.create_loan,
    apirequests.find_student_by_lastname,
    apirequests.make_loan_payment,
    apirequests.update_student_address,
    apirequests.is_accepted_address,
    synthdata.generate_student_profile,
    synthdata.generate_loan_info,
    synthdata.generate_study_info,
    synthdata.generate_bank_info,
    synthdata.generate_communication_info,  
    synthdata.generate_random_education_institution,
    synthdata.generate_random_program_of_study,
    synthdata.generate_random_address,
]

llm_with_tools = llm.bind_tools(tools)

MEMORY_KEY = "chat_history"

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            # "You are very powerful assistant, but bad at managing students, communication, loans, education institutions and programs of study. Can you help me with that?",
            "You are very powerful assistant, but bad at managing students and communication. Can you help me with that?",
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)



async def main():
    chat_history = []

    console = Console()
    layout = Layout()

    def display_header():
        console.print(Panel.fit(
            "[bold blue]Call Centre Agent Assistant[/bold blue]\n"
            "[italic]Ask me anything about managing a student loan![/italic]",
            border_style="cyan"
        ))

    def display_help():
        help_text = """
        **Available Commands:**
        - /help - Show this help message
        - /exit - Exit the application
        
        **Example Questions:**
        - Create a non-registered student with firstname, lastname and home address
        - Add communication info to a non-registered student
        - Create a loan for a non-registered student with loan info, college code and program of study
        - Find a student by last name
        """
        console.print(Markdown(help_text))

    display_header()
    display_help() 

    # Create ProcessPoolExecutor once
    executor = ProcessPoolExecutor() if not debugpy.is_client_connected() else None

    while True:
        try:
            # print("Enter question or type exit to quit")
            user_input = Prompt.ask("\n[bold green]Enter question or type exit to quit[/bold green]")
            if user_input.lower() == '/exit':
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif user_input.lower() == '/help':
                display_help()
                continue
            
            loop = asyncio.get_event_loop()

            if debugpy.is_client_connected():
                console.print("[cyan]Running in debug mode[/cyan]")
                with console.status("[bold blue]Thinking...[/bold blue]"):
                    result = await loop.run_in_executor(None, lambda: agent_executor.invoke({"input": user_input, "chat_history": chat_history}))
            else:
                with console.status("[bold blue]Thinking...[/bold blue]"):
                    result = await loop.run_in_executor(executor, execute_agent,user_input,chat_history)
                
            chat_history.extend(
                [
                    HumanMessage(content=user_input),
                    AIMessage(content=result["output"]),
                ]
            )
            print("\nTools Used:")
            for usage in logger.tool_usage_log:
                print(f"Tool: {usage['tool']}, Input: {usage['input']}")
                
            # print("\n\n Message:\n", result["output"])
            
            console.print(Panel(
                f"[bold white]Message: {result["output"]}[/bold white]",
                border_style="blue"
            ))

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")    
    
    # Ensure the executor is properly shutdown
    if executor:
        executor.shutdown(wait=True)
            

def execute_agent(input_text, history):
    """Execute agent with given input and chat history."""
    return agent_executor.invoke({
        "input": input_text, 
        "chat_history": history
    })

def is_debug_mode() -> bool:
    """Check if running in debug mode."""
    return sys.gettrace() is not None

if __name__ == "__main__":
    asyncio.run(main())