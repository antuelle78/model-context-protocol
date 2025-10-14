import inspect
import json
import httpx
from sqlalchemy.orm import Session
from app import services
from app.api_tool_builder import generate_tools_from_openapi
from app.config import settings

async def get_tool_definitions():
    """Generate a list of tool definitions for all available tools."""
    tool_definitions = []

    for api_config in settings.APIs:
        auth = None
        if api_config.auth_type == "basic":
            auth = httpx.BasicAuth(api_config.auth_user, api_config.auth_pass)
        elif api_config.auth_type == "bearer":
            # For bearer, we still pass it as a header, so we create the header dict here
            auth_headers = {"Authorization": f"Bearer {api_config.auth_key}"}
            # The generate_tools_from_openapi function needs to be able to handle both auth and headers
            # For simplicity in this step, we will assume the builder can handle headers.
            # A better implementation would be to pass the auth object itself.
            api_tools = await generate_tools_from_openapi(api_config.openapi_url, api_name=api_config.name, auth=None) # Auth handled by headers for bearer
        
        api_tools = await generate_tools_from_openapi(api_config.openapi_url, api_name=api_config.name, auth=auth)
        for tool in api_tools:
            tool["annotations"]["api_name"] = api_config.name
        tool_definitions.extend(api_tools)

    # Static tools
    file_tools = [
        {
            "name": "file_fetcher",
            "title": "File Fetcher",
            "description": "Reads all files from a given directory on the network share.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the directory on the network share, relative to the root.",
                    }
                },
                "required": ["path"],
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "encoding": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "annotations": {},
        }
    ]
    
    tool_definitions.extend(file_tools)

    weather_tools = [
        {
            "name": "openweather_get_hourly_forecast",
            "title": "Get Weather Forecast",
            "description": "Fetches the current weather for a specified location.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "number",
                        "description": "The latitude for the location.",
                    },
                    "lon": {
                        "type": "number",
                        "description": "The longitude for the location.",
                    },
                },
                "required": ["lat", "lon"],
            },
            "outputSchema": {"type": "string"},
            "annotations": {},
        }
    ]
    tool_definitions.extend(weather_tools)
    
    return tool_definitions


async def execute_tool(db: Session, tool_name: str, tool_args: dict):
    """Executes a tool by calling the corresponding service function."""
    print(f"Executing tool: {tool_name} with args: {tool_args}")
    try:
        if tool_name == "file_fetcher":
            return services.read_directory(**tool_args)
        elif tool_name == "openweather_get_hourly_forecast":
            return await services.get_weather_forecast(**tool_args)

        # Dynamic API tools
        tool_definitions = await get_tool_definitions()
        tool_def = next((t for t in tool_definitions if t["name"] == tool_name), None)

        if not tool_def:
            return f"Tool {tool_name} not found."

        api_name = tool_def["annotations"]["api_name"]
        api_config = next((api for api in settings.APIs if api.name == api_name), None)

        if not api_config:
            return f"API configuration for {api_name} not found."

        path = tool_def["annotations"]["path"]
        method = tool_def["annotations"]["method"]
        
        auth = None
        if api_config.auth_type == "basic":
            auth = httpx.BasicAuth(api_config.auth_user, api_config.auth_pass)
        elif api_config.auth_type == "bearer":
            auth = None  # Auth is handled by headers for bearer
            headers = {"Authorization": f"Bearer {api_config.auth_key}"}
            return await services.execute_dynamic_api_tool(api_config.base_url, path, method, auth, headers, tool_args)


        return await services.execute_dynamic_api_tool(api_config.base_url, path, method, auth, tool_args)

    except Exception as e:
        import traceback
        print(f"Error executing tool '{tool_name}': {e}")
        traceback.print_exc()
        return f"An error occurred while executing the tool: {e}"
