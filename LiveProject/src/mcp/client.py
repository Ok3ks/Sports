import anyio
from fastmcp import Client

client =  Client("http://127.0.0.1:8000/mcp", verify=False) 

async def main() -> None:
    async with client:
        # List available operations
        # tools = await client.list_tools()
        resources = await client.read_resource("data://2025_2026/")
        print(resources)

if __name__ == "__main__":
    anyio.run(main())