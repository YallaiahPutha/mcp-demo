import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration for the server process
server_params = StdioServerParameters(
    command="python",
    args=["server.py"], # Make sure server.py is in the same directory
)

async def run_mcp_poc():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Initialize session
            await session.initialize()

            # 2. Get available tools from the MCP server
            tools_list = await session.list_tools()
            
            # Format MCP tools for Ollama's tool-calling format
            ollama_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in tools_list.tools
            ]

            print("--- MCP Client Started (Ollama + Tools) ---")
            prompt = input("Ask me anything (e.g., 'What is the weather in Paris and 55 * 12?'): ")

            # 3. Send query + tool definitions to Ollama
            # Use a model that supports tool calling (e.g., llama3.1, mistral)
            response = ollama.chat(
                model='llama3.1',
                messages=[{'role': 'user', 'content': prompt}],
                tools=ollama_tools,
            )

            messages = [{'role': 'user', 'content': prompt}]
            
            # 4. Handle tool calls if Ollama decides to use them
            if response.get('message', {}).get('tool_calls'):
                messages.append(response['message'])
                
                for tool_call in response['message']['tool_calls']:
                    tool_name = tool_call['function']['name']
                    arguments = tool_call['function']['arguments']
                    
                    print(f"[*] Executing Tool: {tool_name} with {arguments}")
                    
                    # Call the tool via MCP
                    result = await session.call_tool(tool_name, arguments)
                    
                    # Add tool result to conversation
                    messages.append({
                        'role': 'tool',
                        'content': str(result.content),
                        'name': tool_name
                    })

                # 5. Get final response from Ollama using the tool data
                final_response = ollama.chat(model='llama3.1', messages=messages)
                print(f"\nAI Response: {final_response['message']['content']}")
            else:
                print(f"\nAI Response: {response['message']['content']}")

if __name__ == "__main__":
    asyncio.run(run_mcp_poc())