from mcp.server.mcpserver import MCPServer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable named "mcp" so `mcp dev` can find it
mcp = MCPServer("My First MCP Server")


@mcp.tool()
async def add_numbers(a: int, b: int) -> str:
    """A tool that sums two numbers."""
    sum = a + b + 10
    return f"The sum of {a} and {b} is {sum} (Calculated by MCP server)."


def main():
    logger.info("Starting My First MCP Server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()