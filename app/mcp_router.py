from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
import json

from app.database import get_db
from app.tool_utils import get_tool_definitions, execute_tool

router = APIRouter()

@router.post("/mcp")
async def mcp_handler(request: Request, db: Session = Depends(get_db)):
    """
    Handles MCP requests.
    """
    try:
        body = await request.json()
        method = body.get("method")
        id = body.get("id")

        if method == "initialize":
            protocol_version = body.get("params", {}).get("protocolVersion", "1.0.0")
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": id,
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
            tools = await get_tool_definitions()
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {"tools": tools},
                }
            )
        elif method == "tools/call":
            tool_name = body["params"]["name"]
            tool_args = body["params"].get("arguments", {})
            tool_response = await execute_tool(db, tool_name, tool_args)
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": tool_response,
                }
            )
        else:
            return JSONResponse(content={"jsonrpc": "2.0", "result": None, "id": id})
    except Exception as e:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {e}"},
                "id": id,
            },
            status_code=500,
        )
