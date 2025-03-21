import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import json
import traceback
import inspect
from weather import mcp, get_alerts, get_forecast  # Import the actual functions directly

app = FastAPI()

@app.post("/call-tool")
async def call_tool(request: Request):
    try:
        data = await request.json()
        tool_name = data.get("tool")
        args = data.get("args", {})
        
        # Log the request for debugging
        print(f"Calling tool: {tool_name} with args: {args}")
        
        if tool_name == "get_alerts":
            state = args.get("state", "")
            if not state:
                return JSONResponse(
                    status_code=400,
                    content={"error": "State parameter is required for get_alerts"}
                )
            # Call the function directly
            result = await get_alerts(state)
            return {"result": result}
        elif tool_name == "get_forecast":
            latitude = args.get("latitude")
            longitude = args.get("longitude")
            if latitude is None or longitude is None:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Latitude and longitude parameters are required for get_forecast"}
                )
            # Call the function directly
            result = await get_forecast(latitude, longitude)
            return {"result": result}
        else:
            return JSONResponse(
                status_code=404,
                content={"error": f"Tool '{tool_name}' not found"}
            )
        
    except Exception as e:
        print(f"Error in call-tool: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback.format_exc()}
        )

@app.get("/list-tools")
async def list_tools():
    try:
        # Hardcode the tools information
        tools = [
            {
                "name": "get_alerts",
                "description": "Get weather alerts for a US state.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "description": "Two-letter US state code (e.g. CA, NY)"}
                    },
                    "required": ["state"]
                }
            },
            {
                "name": "get_forecast",
                "description": "Get weather forecast for a location.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number", "description": "Latitude of the location"},
                        "longitude": {"type": "number", "description": "Longitude of the location"}
                    },
                    "required": ["latitude", "longitude"]
                }
            }
        ]
        return {"tools": tools}
    except Exception as e:
        print(f"Error in list-tools: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback.format_exc()}
        )

@app.get("/")
async def root():
    return {"message": "MCP Weather API is running. Use /list-tools to see available tools."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)