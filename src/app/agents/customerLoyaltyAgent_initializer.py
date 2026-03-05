import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
PROMPT_PATH = os.path.join(project_root, 'prompts', 'CustomerLoyaltyAgentPrompt.txt')
with open(PROMPT_PATH, 'r') as f:
    INSTRUCTIONS = f.read()

define_calculate_discount = FunctionTool(
    name="calculate_discount",
    parameters={
        "type": "object",
        "properties": {
            "CustomerID": {
                "type": "string",
                "description": "The ID of the customer."
            }
        },
        "required": ["CustomerID"],
        "additionalProperties": False
    },
    description="Calculate the discount based on customer loyalty data.",
    strict=True
)

def main():
    endpoint = os.environ.get("FOUNDRY_ENDPOINT")
    if not endpoint:
        raise ValueError("FOUNDRY_ENDPOINT environment variable is required")

    model = os.environ.get("gpt_deployment", "gpt-4o-mini")
    agent_name = os.environ.get("customer_loyalty", "customer-loyalty")

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    with project_client:
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            description="Customer Loyalty Agent that provides personalised discount offers.",
            definition=PromptAgentDefinition(
                model=model,
                instructions=INSTRUCTIONS,
                tools=[define_calculate_discount]
            )
        )
        print(f"Created {agent_name} agent, ID: {agent.id}")

if __name__ == "__main__":
    main()
