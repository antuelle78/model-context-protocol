import inspect
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse, JSONResponse
import io
import time
import uuid
import json


from app.database import get_db, engine
from app.models import Base
from app import services, tools
from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ChatCompletionChoice,
    FetchAllTicketsInput, # New import
    ServiceNowToolInput, # New import
    GLPIToolInput, # New import
)

# ... (rest of the imports)

# Mapping of microservice tool names to their Pydantic input schemas
MICROSERVICE_TOOL_SCHEMAS = {
    "fetch_all_tickets": FetchAllTicketsInput,
    # Add other ServiceNow and GLPI tools here as you create their schemas
}

from pydantic import ValidationError


import httpx # Add httpx for making HTTP requests

# Define ServiceNow tool names and their corresponding microservice endpoints
SERVICENOW_TOOLS = {
    "get_report_open_by_priority": "/servicenow/reports/open_by_priority",
    "get_report_by_assignment_group": "/servicenow/reports/by_assignment_group",
    "get_report_recently_resolved": "/servicenow/reports/recently_resolved",
    "create_new_ticket": "/servicenow/tickets/create",
    "fetch_all_tickets": "/servicenow/tickets/fetch",
}
SERVICENOW_SERVICE_URL = "http://localhost:8001" # URL for the ServiceNow microservice

# Define GLPI tool names and their corresponding microservice endpoints
GLPI_TOOLS = {
    "get_glpi_laptop_count": "/glpi/laptop_count",
    "get_glpi_pc_count": "/glpi/pc_count",
    "get_glpi_monitor_count": "/glpi/monitor_count",
    "get_glpi_os_distribution": "/glpi/os_distribution",
    "get_glpi_full_asset_dump": "/glpi/full_asset_dump",
}
GLPI_SERVICE_URL = "http://localhost:8002" # URL for the GLPI microservice



# Endpoint for chat completions
@app.post("/api/v1/chat/completions")
async def chat_completions(
    request: Request, db: Session = Depends(get_db)
):
    """
    Handles chat completions, including tool calls.
    """
    body = await request.json()
    print(f"Received chat_completions raw request body: {body}")

    # Handle LMstudio initialize method call
    if "jsonrpc" in body:
        if body.get("method") == "initialize":
            protocol_version = body.get("params", {}).get("protocolVersion", "1.0.0")
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "protocolVersion": protocol_version,
                        "capabilities": {
                            "textDocument": {
                                "completion": {
                                    "completionItem": {
                                        "snippetSupport": True
                                    }
                                }
                            }
                        },
                        "serverInfo": {
                            "name": "MCP Server",
                            "version": "1.1.0",
                            "protocolVersion": protocol_version,
                        },
                    },
                }
            )
        elif body.get("method") == "tools/list":
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
            for tool_name in SERVICENOW_TOOLS.keys():
                tool_definitions.append({
                    "name": tool_name,
                    "title": tool_name.replace("_", " ").title(),
                    "description": f"ServiceNow tool: {tool_name}", # Placeholder description
                    "inputSchema": {"type": "object", "properties": {}, "required": []}, # Placeholder schema
                    "outputSchema": {"type": "object", "properties": {}},
                    "annotations": {},
                })

            # Add GLPI tools
            for tool_name in GLPI_TOOLS.keys():
                tool_definitions.append({
                    "name": tool_name,
                    "title": tool_name.replace("_", " ").title(),
                    "description": f"GLPI tool: {tool_name}", # Placeholder description
                    "inputSchema": {"type": "object", "properties": {}, "required": []}, # Placeholder schema
                    "outputSchema": {"type": "object", "properties": {}},
                    "annotations": {},
                })

            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {"tools": tool_definitions},
                }
            )
        elif body.get("method") == "tools/list":
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
            for tool_name in SERVICENOW_TOOLS.keys():
                tool_definitions.append({
                    "name": tool_name,
                    "title": tool_name.replace("_", " ").title(),
                    "description": f"ServiceNow tool: {tool_name}", # Placeholder description
                    "inputSchema": {"type": "object", "properties": {}, "required": []}, # Placeholder schema
                    "outputSchema": {"type": "object", "properties": {}},
                    "annotations": {},
                })

            # Add GLPI tools
            for tool_name in GLPI_TOOLS.keys():
                tool_definitions.append({
                    "name": tool_name,
                    "title": tool_name.replace("_", " ").title(),
                    "description": f"GLPI tool: {tool_name}", # Placeholder description
                    "inputSchema": {"type": "object", "properties": {}, "required": []}, # Placeholder schema
                    "outputSchema": {"type": "object", "properties": {}},
                    "annotations": {},
                })

            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {"tools": tool_definitions},
                }
            )
        else:
            return JSONResponse(content={"jsonrpc": "2.0", "result": None, "id": body.get("id")})

    # Process as ChatCompletionRequest
    chat_request = ChatCompletionRequest(**body)
    last_message = chat_request.messages[-1]
    
    tool_name = None
    tool_args = {}

    if last_message.tool_calls:
        # If tool_calls are present, use the first one
        tool_call_obj = last_message.tool_calls[0]
        tool_name = tool_call_obj.function.name
        tool_args = json.loads(tool_call_obj.function.arguments)
        print(f"Extracted tool call from tool_calls: {tool_name} with args: {tool_args}")
    elif last_message.content:
        # Fallback to parsing content if tool_calls are not present
        try:
            tool_call = json.loads(last_message.content)
            tool_name = tool_call["name"]
            tool_args_str = tool_call.get("arguments", "{}")
            if isinstance(tool_args_str, str):
                tool_args = json.loads(tool_args_str)
            else:
                tool_args = tool_args_str
            print(f"Extracted tool call from content: {tool_name} with args: {tool_args}")
        except json.JSONDecodeError:
            # If content is not a valid JSON, it's a regular chat message
            response_message = ChatMessage(
                role="assistant",
                content="I'm sorry, I can only process tool calls or regular chat messages. Your last message was not a valid tool call.",
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
    else:
        response_message = ChatMessage(
            role="assistant",
            content="I'm sorry, I couldn't understand your request. Please provide a valid tool call or a chat message.",
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

    try:
        tool_response = None

        if tool_name in SERVICENOW_TOOLS:

            
            print(f"Calling ServiceNow microservice for tool: {tool_name}")
            async with httpx.AsyncClient() as client:
                endpoint = SERVICENOW_TOOLS[tool_name]
                request_url = f"{SERVICENOW_SERVICE_URL}{endpoint}"
                print(f"ServiceNow microservice request URL: {request_url}")
                if tool_name in ["get_report_recently_resolved", "get_report_open_by_priority", "get_report_by_assignment_group"]:
                    print(f"Making GET request to {request_url}")
                    response = await client.get(request_url, params=tool_args)
                else:
                    print(f"Making POST request to {request_url} with data: {tool_args}")
                    response = await client.post(request_url, json=tool_args)
                response.raise_for_status()
                tool_response = response.json()
                print(f"ServiceNow microservice response: {tool_response}")
        elif tool_name in GLPI_TOOLS:

            
            print(f"Calling GLPI microservice for tool: {tool_name}")
            async with httpx.AsyncClient() as client:
                endpoint = GLPI_TOOLS[tool_name]
                # All GLPI tools are GET requests for now, except full_asset_dump which is POST
                if tool_name == "get_glpi_full_asset_dump":
                    response = await client.post(f"{GLPI_SERVICE_URL}{endpoint}", json=tool_args)
                else:
                    response = await client.get(f"{GLPI_SERVICE_URL}{endpoint}")
                response.raise_for_status()
                tool_response = response.json()
        else:
            # Call the local tool
            tool_response = await tools.call_tool(db, tool_name, tool_args)

        if isinstance(tool_response, dict):
            tool_response = json.dumps(tool_response, indent=2)

        response_message = ChatMessage(
            role="assistant",
            content=tool_response,
        )
    except json.JSONDecodeError:
        response_message = ChatMessage(
            role="assistant",
            content="Invalid JSON format in tool call.",
        )
    except KeyError as e:
        response_message = ChatMessage(
            role="assistant",
            content=f"Missing key in tool call: {e}",
        )
    except httpx.RequestError as e:
        print(f"HTTP request error to microservice: {e}")
        response_message = ChatMessage(
            role="assistant",
            content=f"Error communicating with microservice: {e}",
        )
    except httpx.HTTPStatusError as e:
        print(f"HTTP status error from microservice: {e.response.status_code} - {e.response.text}")
        response_message = ChatMessage(
            role="assistant",
            content=f"Microservice returned an error: {e.response.status_code} - {e.response.text}",
        )
    except Exception as e:
        print(f"Error processing tool call: {e}")
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