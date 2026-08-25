import json
from pathlib import Path
import anyio
import logfire
from fastmcp import Client
from pydantic_ai import Agent
from fastmcp.server import FastMCP
from pydantic_core import to_jsonable_python 
from pydantic_ai.mcp import MCPToolset
from src.mcp.app import Season


client =  Client("http://127.0.0.1:8000/mcp", verify=False) 
server = MCPToolset(client=client, cache_tools=False)

DATA_ANALYST_PROMPT = f"""

You're a top data analyst, your duty is to find the devil in the detail, and assist this user in filtering through the noise
Available to you are mcp servers containing the prompts, resources and tools present.  It's paramount that you are truthful, only respond
if you're connected to a mcp server

Before doing anything, list all available tools, resources, and prompts you have access to.

**Resources** → What data do I have access to?
**Prompts** → Are there predefined templates relevant to the task?
**Tools** → What actions have been pre-made for this data, otherwise write custom python analysis code

Seasons are defined of type {Season}, where required, use seaborn to visualize outputs
"""


async def main():
  """ Tests MCP with prompts """
  user_input = input("User:")
  history = []
  while user_input != "":
      agent = Agent(
              "anthropic:claude-opus-4-6",
              retries=1,
              system_prompt=(DATA_ANALYST_PROMPT),
              toolsets=[server],
          )
      # agent.set_mcp_sampling_model() 

      async with agent:
        response = await agent.run(user_prompt=user_input, message_history=history)
        print(response.output)
        history = response.all_messages()
        user_input = input("What next will you like me to do?")

if __name__ == "__main__":
  logfire.configure()
  logfire.instrument_pydantic_ai()
  anyio.run(main)

  
