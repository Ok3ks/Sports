import json
from pathlib import Path
import anyio
from fastmcp import Client
from pydantic_ai import Agent
from pydantic_core import to_jsonable_python 


client =  Client("http://127.0.0.1:8000/mcp", verify=False) 


async def main() -> None:
    async with client:
        # List available operations
        tools = await client.list_tools()
        prompts = await client.list_prompts()
        # resources = await client.read_resource("data://2025_2026/")
        print(prompts)
        print(tools)

if __name__ == "__main__":
    anyio.run(main())