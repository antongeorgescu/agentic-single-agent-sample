# Agentic AI Multi-Agent Assistant

A conversational AI assistant for call center operations that helps manage student information, loans, and communications using Azure OpenAI and LangChain.

## Features

- Create and manage non-registered student profiles
- Handle student communication information
- Process student loan applications
- Search for students by last name
- Generate synthetic data for testing
- Interactive command-line interface with Rich text formatting

## Concept Design

The solution is Agentic AI centric, with the user interface business logic controlled on-fly by prompts provided either by manual operator or automation job.


![Image](https://github.com/user-attachments/assets/6eac2a79-dd35-4e42-ba25-ffd5eccf982d)

## High-level Design Diagram

The design contains four AI Agentic agents that are specialized for different tasks and can communicate with each other:
* **API Agent** selects the right API endpoint and provides the required parameters extracted from the prompt
* **Synth Data Agent** generates the data required for test in cvarious formats specified in the prompt
* **Database Agent** queries the data in the database after a select or an update operation triggered by **API Agent**, and validates it
* **QA Agent** reads the openapi.yaml file and provides a test plan according to the prompt requirements. It also collects the tests results and renders reports back to the user as per prompt. 

![Image](https://github.com/user-attachments/assets/a8684849-211e-4af8-82bb-f4b838e95243)

## Multiple Agent Collaboration

The four agents collaborate with each other in many ways. They invoke each other by using **dynamic agent invocation** The following code sample captures one of the possible scenarios:

```
from langchain.agents import ApiRequestAgent, SynthDataAgent

# Define agent descriptions
agents = {
    "ApiRequestAgent": {
        "description": "Make requests to a wide variety of API endpoints.",
        "agent": ApiRequestAgent()
    },
    "SynthDataAgent": {
        "description": "Generates synthetic data used for test automation.",
        "agent": SynthDataAgent()
    }
}

# Function to invoke agent based on description
def invoke_agent(agent_name, *args, **kwargs):
    agent_info = agents.get(agent_name)
    if agent_info:
        print(f"Invoking {agent_name}: {agent_info['description']}")
        return agent_info'agent'
    else:
        raise ValueError(f"Agent {agent_name} not found.")

# Example usage
data_request = "Get a student profile with synthetic data."
synth_data = invoke_agent("SynthDataAgent", data_request)
api_request = "Use the data to create a non-registered student record and add a communication profile with preference set to SMS."
api_result = invoke_agent("ApiRequestAgent", api_request)

print(api_result)
```

The following diagram shows a scenario with 4 agents that collaborate with each other:

![Image](https://github.com/user-attachments/assets/b47f837f-c623-4a6f-84b4-b25df9328d80)

## Prerequisites

- Python 3.x
- Azure OpenAI API access
- Required environment variables:
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_DEPLOYMENT_NAME`
  - `AZURE_OPENAI_API_VERSION`

## Installation

1. Clone the repository
2. Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage

1. Set up your environment variables in `.env` file
2. Run the application:
```sh
python src/ccagent.py
```

### Available Commands

- `/help` - Show help message
- `/exit` - Exit the application

### Example Questions

- Create a non-registered student with firstname, lastname and home address
- Add communication info to a non-registered student
- Create a loan for a non-registered student with loan info, college code and program of study
- Find a student by last name

## Project Structure

```
.
├── references/
│   ├── openapi.yaml        # API specification
│   └── testplan.txt        # API test plan
├── src/
│   ├── ccagent.py         # Main application file
│   ├── tools/
│   │   ├── ccactions.py   # Core business actions
│   │   └── synthdata.py   # Synthetic data generation
│   └── utils/
│       ├── logger.py      # Logging utilities
│       └── question_samples.txt  # Sample test scenarios
├── tests/
│   └── test_ccagent.py    # Unit tests
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
└── requirements.txt      # Project dependencies
```

Key components:
- `src/` - Source code directory
  - `ccagent.py` - Main application with CLI interface
  - `tools/` - Core functionality modules
  - `utils/` - Helper utilities and logging
- `references/` - API documentation and test plans
- `tests/` - Test suites and test data

## Dependencies

Key dependencies include:
- langchain
- openai
- rich (for CLI formatting)
- faker (for synthetic data)
- python-dotenv

For a complete list, see `requirements.txt`.