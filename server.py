from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
import httpx

# Initialize the MCP Server
mcp = FastMCP("MyPoCServer")

# --- Tool 1: Arithmetic ---
@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluate a simple mathematical expression (e.g., '2 + 2' or '10 * 5')."""
    try:
        # Note: In production, use a safer math parser
        result = eval(expression, {"__builtins__": None}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Tool 2: Weather ---
@mcp.tool()
async def get_weather(city: str) -> str:
    """Fetch current weather for a specific city."""
    url = f"https://wttr.in/{city}?format=3"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.text.strip()
        return f"Could not fetch weather for {city}."

# --- Tool 3: DuckDuckGo Search ---
@mcp.tool()
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo for real-time information."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
        if not results:
            return "No results found."
        return "\n".join([f"{r['title']}: {r['body']} ({r['href']})" for r in results])

if __name__ == "__main__":
    # Start the server using stdio transport
    mcp.run(transport="stdio")