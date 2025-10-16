
from fastapi import FastAPI, APIRouter, Request
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import os

# --- Pydantic Schemas ---
class GetWeatherArgs(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")

# --- Tool Implementation ---
async def get_weather_forecast(args: GetWeatherArgs):
    """
    Fetches the current weather for a specified location using OpenWeatherMap.
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "OpenWeather API key is not configured."

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={args.lat}&lon={args.lon}&appid={api_key}"
    try:
        async with requests.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            if response.status_code == 200:
                return f"Current weather: {data['weather'][0]['description']}, temperature: {data['main']['temp'] - 273.15:.2f}°C"
            else:
                return f"Could not get weather data. Response: {data}"
    except Exception as e:
        return f"An error occurred: {e}"

# --- MCP Router ---
router = APIRouter()

@router.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method")
    id = body.get("id")

    if method == "initialize":
        return JSONResponse(content={
            "jsonrpc": "2.0", "id": id,
            "result": {"protocolVersion": "1.0.0", "serverInfo": {"name": "Weather Tool"}}
        })
    elif method == "tools/list":
        tools = [{
            "name": "get_weather_forecast",
            "title": "Get Weather Forecast",
            "description": "Fetches the current weather for a specified location.",
            "inputSchema": GetWeatherArgs.model_json_schema(),
            "outputSchema": {"type": "string"}
        }]
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": {"tools": tools}})
    elif method == "tools/call":
        tool_name = body["params"]["name"]
        tool_args = body["params"].get("arguments", {})
        if tool_name == "get_weather_forecast":
            args = GetWeatherArgs(**tool_args)
            result = await get_weather_forecast(args)
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        else:
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32601, "message": "Method not found"}}, status_code=404)
    else:
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": None})

# --- FastAPI App ---
app = FastAPI()
app.include_router(router, prefix="/api/v1")
