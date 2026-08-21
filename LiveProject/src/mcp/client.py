import anyio
from fastmcp import Client

client =  Client("http://127.0.0.1:8000/mcp", verify=False) 
async def main() -> None:
    async with client:
          # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        print(tools)
        print(resources)
        print(prompts)

if __name__ == "__main__":
    anyio.run(main)