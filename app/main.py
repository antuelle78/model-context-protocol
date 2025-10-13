from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
import inspect
import time
import uuid
import json
import httpx

from app.database import get_db
from app import tools
from app.config import settings
from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ChatCompletionChoice,
    GetReportOpenByPriorityArgs,
    GetReportByAssignmentGroupArgs,
    CreateNewTicketServiceNowArgs,
    GetGlpiFullAssetDumpArgs,
)

app = FastAPI()

# Define tool names and their corresponding microservice endpoints and schemas
SERVICENOW_TOOLS = {
    "get_report_open_by_priority": {
        "endpoint": "/servicenow/reports/open_by_priority",
        "description": "Get a report of open tickets by priority in ServiceNow.",
        "schema": GetReportOpenByPriorityArgs,
    },
    "get_report_by_assignment_group": {
        "endpoint": "/servicenow/reports/by_assignment_group",
        "description": "Get a report of tickets by assignment group in ServiceNow.",
        "schema": GetReportByAssignmentGroupArgs,
    },
    "get_report_recently_resolved": {
        "endpoint": "/servicenow/reports/recently_resolved",
        "description": "Get a report of recently resolved tickets in ServiceNow.",
        "schema": None, # No specific arguments
    },
    "create_new_ticket": {
        "endpoint": "/servicenow/tickets/create",
        "description": "Create a new ticket in ServiceNow.",
        "schema": CreateNewTicketServiceNowArgs,
    },
    "fetch_all_servicenow_tickets": {
        "endpoint": "/servicenow/tickets/fetch_all_servicenow_tickets",
        "description": "Fetch all tickets from ServiceNow.",
        "schema": None, # No specific arguments
    },
}

GLPI_TOOLS = {
    "get_glpi_laptop_count": {
        "endpoint": "/glpi/laptop_count",
        "description": "Get the count of laptops in GLPI.",
        "schema": None,
    },
    "get_glpi_pc_count": {
        "endpoint": "/glpi/pc_count",
        "description": "Get the count of PCs in GLPI.",
        "schema": None,
    },
    "get_glpi_monitor_count": {
        "endpoint": "/glpi/monitor_count",
        "description": "Get the count of monitors in GLPI.",
        "schema": None,
    },
    "get_glpi_os_distribution": {
        "endpoint": "/glpi/os_distribution",
        "description": "Get the OS distribution of assets in GLPI.",
        "schema": None,
    },
    "get_glpi_full_asset_dump": {
        "endpoint": "/glpi/full_asset_dump",
        "description": "Get a full asset dump from GLPI.",
        "schema": GetGlpiFullAssetDumpArgs,
    },
    "fetch_all_glpi_inventory": {
        "endpoint": "/glpi/inventory",
        "description": "Fetch all inventory from GLPI.",
        "schema": None,
    },
}


def get_tool_definitions():
    """Generate a list of tool definitions for all available tools."""
    tool_definitions = []

    # Add tools from the local 'tools' module
    for tool_name, tool_func in tools.tools.items():
        signature = inspect.signature(tool_func)
        parameters = signature.parameters

        input_properties = {}
        required_params = []
        for name, param in parameters.items():
            if name == "db":
                continue
            input_properties[name] = {"type": "string"}
            if param.default == inspect.Parameter.empty:
                required_params.append(name)

        tool_definitions.append({
            "name": tool_name,
            "title": tool_name.replace("_", " ").title(),
            "description": tool_func.__doc__.strip() if tool_func.__doc__ else "",
            "inputSchema": {
                "type": "object",
                "properties": input_properties,
                "required": required_params,
            },
            "outputSchema": {"type": "object", "properties": {}},
            "annotations": {},
        })

    # Add ServiceNow tools
    for tool_name, tool_info in SERVICENOW_TOOLS.items():
        input_schema = {"type": "object", "properties": {}, "required": []}
        if tool_info["schema"]:
            input_schema = tool_info["schema"].model_json_schema()

        tool_definitions.append({
            "name": tool_name,
            "title": tool_name.replace("_", " ").title(),
            "description": tool_info["description"],
            "inputSchema": input_schema,
            "outputSchema": {"type": "object", "properties": {"message": {"type": "string"}}},
            "annotations": {},
        })

    # Add GLPI tools
    for tool_name, tool_info in GLPI_TOOLS.items():
        input_schema = {"type": "object", "properties": {}, "required": []}
        if tool_info["schema"]:
            input_schema = tool_info["schema"].model_json_schema()

        tool_definitions.append({
            "name": tool_name,
            "title": tool_name.replace("_", " ").title(),
            "description": tool_info["description"],
            "inputSchema": input_schema,
            "outputSchema": {"type": "object", "properties": {}},
            "annotations": {},
        })

    return tool_definitions


@app.post("/api/v1/chat/completions")
async def chat_completions(request: Request, db: Session = Depends(get_db)):
    """
    Handles chat completions, including tool calls for both local and microservice tools.
    """
    print("Entering chat_completions")
    try:
        raw_body = await request.body()
        print(f"Received raw request body: {raw_body.decode()}")
        body = json.loads(raw_body)
        print(f"Parsed request body: {body}")

        # Handle MCP (LMStudio) specific methods
        if "jsonrpc" in body:
            method = body.get("method")
            if method == "initialize":
                protocol_version = body.get("params", {}).get("protocolVersion", "1.0.0")
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {
                            "protocolVersion": protocol_version,
                            "serverInfo": {
                                "name": "MCP Server",
                                "version": "1.1.0",
                                "protocolVersion": protocol_version,
                            },
                            "capabilities": {
                                "textDocument": {
                                    "completion": {
                                        "completionItem": {
                                            "snippetSupport": True
                                        }
                                    }
                                }
                            }
                        },
                    }
                )
            elif method == "tools/list":
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": {"tools": get_tool_definitions()},
                    }
                )
            elif method == "tools/call":
                tool_name = body["params"]["name"]
                tool_args = body["params"].get("arguments", {})
                print(f"Calling execute_tool with tool_name: {tool_name}")
                tool_response = await execute_tool(db, tool_name, tool_args)
                print(f"Received tool_response: {tool_response}")
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "result": tool_response,
                    }
                )
            else:
                return JSONResponse(content={"jsonrpc": "2.0", "result": None, "id": body.get("id")})

        # Process as a standard ChatCompletionRequest
        print("Processing as ChatCompletionRequest")
        chat_request = ChatCompletionRequest(**body)
        last_message = chat_request.messages[-1]

        tool_name = None
        tool_args = {}

        if chat_request.tool_calls:
            print("Extracting tool call from tool_calls")
            tool_call_obj = chat_request.tool_calls[0]
            tool_name = tool_call_obj.function.name
            tool_args = json.loads(tool_call_obj.function.arguments)
            print(f"Extracted tool call from tool_calls: {tool_name} with args: {tool_args}")
        elif last_message.content:
            print("Extracting tool call from content")
            try:
                tool_call = json.loads(last_message.content)
                tool_name = tool_call["name"]
                tool_args_str = tool_call.get("arguments", "{}")
                tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
                print(f"Extracted tool call from content: {tool_name} with args: {tool_args}")
            except json.JSONDecodeError:
                # Not a tool call, treat as a regular message (or handle as error)
                print("Could not decode JSON from content")
                pass

        if not tool_name:
            print("Tool name not found")
            # Handle cases where no tool call is identified
            response_message = ChatMessage(
                role="assistant",
                content="I'm sorry, I couldn't identify a tool to call. Please try again.",
            )
        else:
            print(f"Calling execute_tool with tool_name: {tool_name}")
            tool_response = await execute_tool(db, tool_name, tool_args)
            print(f"Received tool_response: {tool_response}")
            response_message = ChatMessage(role="assistant", content=tool_response)

    except Exception as e:
        print(f"Error in chat_completions: {e}")
        response_message = ChatMessage(
            role="assistant",
            content=f"An unexpected error occurred: {e}",
        )

    return ChatCompletionResponse(
        id=str(uuid.uuid4()),
        object="chat.completion",
        created=int(time.time()),
        model=chat_request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=response_message,
                finish_reason="stop",
            )
        ],
    )


async def execute_tool(db: Session, tool_name: str, tool_args: dict):
    """Executes a tool either locally or by calling a microservice."""
    print(f"Executing tool: {tool_name} with args: {tool_args}")
    try:
        cleaned_tool_args = {k: v for k, v in tool_args.items() if k not in ["method", "result", "id"]}

        if tool_name in SERVICENOW_TOOLS:
            return await call_microservice(
                settings.SERVICENOW_SERVICE_URL,
                SERVICENOW_TOOLS[tool_name]["endpoint"],
                cleaned_tool_args,
            )
        elif tool_name in GLPI_TOOLS:
            return await call_microservice(
                settings.GLPI_SERVICE_URL,
                GLPI_TOOLS[tool_name]["endpoint"],
                cleaned_tool_args,
            )
        else:
            # Call a local tool
            tool_response = await tools.call_tool(db, tool_name, cleaned_tool_args)
            return json.dumps(tool_response, indent=2) if isinstance(tool_response, dict) else tool_response

    except Exception as e:
        print(f"Error executing tool '{tool_name}': {e}")
        return f"An error occurred while executing the tool: {e}"


async def call_microservice(base_url: str, endpoint: str, args: dict):
    """Generic function to call a microservice endpoint."""
    request_url = f"{base_url}{endpoint}"
    print(f"Calling microservice at: {request_url} with args: {args}")
    async with httpx.AsyncClient() as client:
        try:
            # Determine if it's a GET or POST request based on the tool
            if "create" in endpoint or "fetch" in endpoint:
                response = await client.post(request_url, json=args)
            else:
                response = await client.get(request_url, params=args)
            
            response.raise_for_status()
            print(f"Microservice raw response: {response.text}")
            return response.json()
        except httpx.RequestError as e:
            print(f"HTTP request error to microservice: {e}")
            return f"Error communicating with microservice: {e}"
        except httpx.HTTPStatusError as e:
            print(f"HTTP status error from microservice: {e.response.status_code} - {e.response.text}")
            return f"Microservice returned an error: {e.response.status_code} - {e.response.text}"
