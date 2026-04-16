from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

app = FastAPI(title="MCP Ollama API")

# Define the request structure
class Query(BaseModel):
    prompt: str

# Configuration for the server process (ensure server.py is in the same folder)
server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)

async def process_mcp_request(user_prompt: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Get tools from MCP Server
            tools_list = await session.list_tools()
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

            # 2. Initial call to Ollama
            messages = [{'role': 'user', 'content': user_prompt}]
            response = ollama.chat(
                model='llama3.1',
                messages=messages,
                tools=ollama_tools,
            )

            # 3. Check if tools are needed
            if response.get('message', {}).get('tool_calls'):
                messages.append(response['message'])
                
                for tool_call in response['message']['tool_calls']:
                    tool_name = tool_call['function']['name']
                    arguments = tool_call['function']['arguments']
                    
                    # Execute MCP Tool
                    result = await session.call_tool(tool_name, arguments)
                    
                    messages.append({
                        'role': 'tool',
                        'content': str(result.content),
                        'name': tool_name
                    })

                # 4. Final response with tool data
                final_response = ollama.chat(model='llama3.1', messages=messages)
                return final_response['message']['content']
            
            return response['message']['content']

@app.post("/ask")
async def ask_ai(query: Query):
    try:
        answer = await process_mcp_request(query.prompt)
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)