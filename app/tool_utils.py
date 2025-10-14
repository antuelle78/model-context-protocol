import inspect
import json
import httpx
from sqlalchemy.orm import Session
from app import services, yahoo_finance_tools
from app.api_tool_builder import generate_tools_from_openapi
from app.config import settings
from app.schemas import GetStockPriceArgs

# Mapping of tool names to their argument schemas
tool_arg_schemas = {
    "get_stock_price": GetStockPriceArgs,
}

def get_input_schema(tool_name):
    """Get the input schema for a given tool based on its Pydantic model."""
    if tool_name in tool_arg_schemas:
        return tool_arg_schemas[tool_name].model_json_schema()
    return {"type": "object", "properties": {}}

async def get_tool_definitions():
    """Generate a list of tool definitions for all available tools."""
    tool_definitions = []

    # Dynamic tools from OpenAPI specs
    for api_config in settings.APIs:
        auth = None
        if api_config.auth_type == "basic":
            auth = httpx.BasicAuth(api_config.auth_user, api_config.auth_pass)
        
        api_tools = await generate_tools_from_openapi(api_config.openapi_url, api_name=api_config.name, auth=auth)
        for tool in api_tools:
            tool["annotations"]["api_name"] = api_config.name
        tool_definitions.extend(api_tools)

    # Static tools from modules
    tool_modules = [yahoo_finance_tools]
    for module in tool_modules:
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("_"):  # Exclude private functions
                tool_definitions.append({
                    "name": name,
                    "title": name.replace("_", " ").title(),
                    "description": inspect.getdoc(func),
                    "inputSchema": get_input_schema(name),
                    "outputSchema": {"type": "string"},
                    "annotations": {"module": module.__name__},
                })

    # Manually defined tools
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
        # Manually defined tools
        if tool_name == "file_fetcher":
            return services.read_directory(**tool_args)
        elif tool_name == "openweather_get_hourly_forecast":
            return await services.get_weather_forecast(**tool_args)

        # Tools from modules
        tool_definitions = await get_tool_definitions()
        tool_def = next((t for t in tool_definitions if t["name"] == tool_name), None)

        if not tool_def:
            return f"Tool {tool_name} not found."

        if "module" in tool_def["annotations"]:
            module_name = tool_def["annotations"]["module"]
            module = {
                "app.yahoo_finance_tools": yahoo_finance_tools,
            }.get(module_name)

            if module:
                func = getattr(module, tool_name)
                
                # Instantiate the correct Pydantic model for the arguments
                if tool_name in tool_arg_schemas:
                    args_model = tool_arg_schemas[tool_name](**tool_args)
                    tool_args = {'args': args_model}

                # For async functions
                if inspect.iscoroutinefunction(func):
                     # Check if the function requires a db session
                    if "db" in inspect.signature(func).parameters:
                        return await func(db=db, **tool_args)
                    else:
                        return await func(**tool_args)
                # For sync functions
                else:
                    # Check if the function requires a db session
                    if "db" in inspect.signature(func).parameters:
                        return func(db=db, **tool_args)
                    else:
                        return func(**tool_args)

        # Dynamic API tools
        if "api_name" in tool_def["annotations"]:
            api_name = tool_def["annotations"]["api_name"]
            api_config = next((api for api in settings.APIs if api.name == api_name), None)

            if not api_config:
                return f"API configuration for {api_name} not found."

            path = tool_def["annotations"]["path"]
            method = tool_def["annotations"]["method"]
            
            auth = None
            headers = {}
            if api_config.auth_type == "basic":
                auth = httpx.BasicAuth(api_config.auth_user, api_config.auth_pass)
            elif api_config.auth_type == "bearer":
                headers = {"Authorization": f"Bearer {api_config.auth_key}"}

            return await services.execute_dynamic_api_tool(api_config.base_url, path, method, auth, headers, tool_args)

        return f"Tool {tool_name} not found or could not be executed."

    except Exception as e:
        import traceback
        print(f"Error executing tool '{tool_name}': {e}")
        traceback.print_exc()
        return f"An error occurred while executing the tool: {e}"
