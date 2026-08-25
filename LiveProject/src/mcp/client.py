"""
  Sample to code which creates a client to verify presence of tools, prompts created in app.py
"""


import anyio
from fastmcp import Client

client =  Client("http://127.0.0.1:8000/mcp", verify=False) 


async def main() -> None:
    async with client:
        # List available operations
        tools = await client.list_tools()
        prompts = await client.list_prompts()
        print(prompts)
        print(tools)

if __name__ == "__main__":
    anyio.run(main())