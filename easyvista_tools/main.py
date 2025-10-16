
from fastapi import FastAPI, APIRouter, Request
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import os
import json

# --- Pydantic Schemas ---
class CreateTicketArgs(BaseModel):
    catalog_code: str = Field(..., description="The catalog code of the ticket.")
    description: str = Field(..., description="The description of the ticket.")
    urgency_id: int = Field(..., description="The urgency ID of the ticket.")
    severity_id: int = Field(..., description="The severity ID of the ticket.")
    requestor_mail: str = Field(..., description="The email of the requestor.")
    requestor_name: str = Field(..., description="The name of the requestor.")

class GetTicketArgs(BaseModel):
    rfc_number: str = Field(..., description="The RFC number of the ticket.")

class UpdateTicketArgs(BaseModel):
    rfc_number: str = Field(..., description="The RFC number of the ticket.")
    params: dict = Field(..., description="The parameters to update.")

class CloseTicketArgs(BaseModel):
    rfc_number: str = Field(..., description="The RFC number of the ticket.")
    comment: str = Field(..., description="The closing comment.")

# --- Tool Implementation ---
def create_ticket(args: CreateTicketArgs):
    """
    Creates a new EasyVista ticket.
    """
    easyvista_url = os.environ.get("EASYVISTA_URL")
    api_key = os.environ.get("EASYVISTA_API_KEY")
    account_id = os.environ.get("EASYVISTA_ACCOUNT_ID")

    if not easyvista_url or not api_key or not account_id:
        return "EasyVista URL, API key, or account ID is not configured."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "account_id": account_id,
        "catalog_code": args.catalog_code,
        "description": args.description,
        "urgency_id": args.urgency_id,
        "severity_id": args.severity_id,
        "requestor_mail": args.requestor_mail,
        "requestor_name": args.requestor_name
    }

    try:
        response = requests.post(f"{easyvista_url}/api/v1/tickets", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def get_ticket(args: GetTicketArgs):
    """
    Retrieves an EasyVista ticket.
    """
    easyvista_url = os.environ.get("EASYVISTA_URL")
    api_key = os.environ.get("EASYVISTA_API_KEY")
    account_id = os.environ.get("EASYVISTA_ACCOUNT_ID")

    if not easyvista_url or not api_key or not account_id:
        return "EasyVista URL, API key, or account ID is not configured."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{easyvista_url}/api/v1/tickets/{args.rfc_number}?account_id={account_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def update_ticket(args: UpdateTicketArgs):
    """
    Updates an EasyVista ticket.
    """
    easyvista_url = os.environ.get("EASYVISTA_URL")
    api_key = os.environ.get("EASYVISTA_API_KEY")
    account_id = os.environ.get("EASYVISTA_ACCOUNT_ID")

    if not easyvista_url or not api_key or not account_id:
        return "EasyVista URL, API key, or account ID is not configured."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "account_id": account_id,
        **args.params
    }

    try:
        response = requests.put(f"{easyvista_url}/api/v1/tickets/{args.rfc_number}", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def close_ticket(args: CloseTicketArgs):
    """
    Closes an EasyVista ticket.
    """
    easyvista_url = os.environ.get("EASYVISTA_URL")
    api_key = os.environ.get("EASYVISTA_API_KEY")
    account_id = os.environ.get("EASYVISTA_ACCOUNT_ID")

    if not easyvista_url or not api_key or not account_id:
        return "EasyVista URL, API key, or account ID is not configured."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "account_id": account_id,
        "status": "Closed",
        "comment": args.comment
    }

    try:
        response = requests.put(f"{easyvista_url}/api/v1/tickets/{args.rfc_number}", headers=headers, a=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
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
            "result": {"protocolVersion": "1.0.0", "serverInfo": {"name": "EasyVista Tool"}}
        })
    elif method == "tools/list":
        tools = [
            {
                "name": "create_ticket",
                "title": "Create EasyVista Ticket",
                "description": "Creates a new EasyVista ticket.",
                "inputSchema": CreateTicketArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "get_ticket",
                "title": "Get EasyVista Ticket",
                "description": "Retrieves an EasyVista ticket.",
                "inputSchema": GetTicketArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "update_ticket",
                "title": "Update EasyVista Ticket",
                "description": "Updates an EasyVista ticket.",
                "inputSchema": UpdateTicketArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "close_ticket",
                "title": "Close EasyVista Ticket",
                "description": "Closes an EasyVista ticket.",
                "inputSchema": CloseTicketArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            }
        ]
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": {"tools": tools}})
    elif method == "tools/call":
        tool_name = body["params"]["name"]
        tool_args = body["params"].get("arguments", {})
        if tool_name == "create_ticket":
            args = CreateTicketArgs(**tool_args)
            result = create_ticket(args)
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "get_ticket":
            args = GetTicketArgs(**tool_args)
            result = get_ticket(args)
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "update_ticket":
            args = UpdateTicketArgs(**tool_args)
            result = update_ticket(args)
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "close_ticket":
            args = CloseTicketArgs(**tool_args)
            result = close_ticket(args)
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        else:
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32601, "message": "Method not found"}}, status_code=404)
    else:
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": None})

# --- FastAPI App ---
app = FastAPI()
app.include_router(router, prefix="/api/v1")
