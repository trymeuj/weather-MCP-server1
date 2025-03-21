import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
import json
from weather import mcp

app = FastAPI()

@app.post("/call-tool")
async def call_tool(request: Request):
    data = await request.json()
    tool_name = data.get("tool")
    args = data.get("args", {})
    
    if tool_name == "get_alerts":
        result = await mcp.tools["get_alerts"](args.get("state"))
        return {"result": result}
    elif tool_name == "get_forecast":
        result = await mcp.tools["get_forecast"](args.get("latitude"), args.get("longitude"))
        return {"result": result}
    else:
        return {"error": "Tool not found"}

@app.get("/list-tools")
async def list_tools():
    tools = []
    for name, tool in mcp.tools.items():
        tools.append({
            "name": name,
            "description": tool.__doc__,
            "inputSchema": mcp.get_tool_schema(name)
        })
    return {"tools": tools}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)