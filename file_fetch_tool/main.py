
from fastapi import FastAPI, APIRouter, Request
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field
import os
import base64

# --- Pydantic Schemas ---
class FileFetchArgs(BaseModel):
    path: str = Field(..., description="The path to the directory on the network share.")

# --- Tool Implementation ---
def read_directory(path: str):
    """
    Reads all files from a given directory on the network share and returns their content.
    """
    base_path = "/home/mnelson-ext/model-context-protocol/network_share"
    full_path = os.path.join(base_path, path)
    results = {}
    if not os.path.isdir(full_path):
        return {"error": "Path is not a directory or does not exist."}

    for filename in os.listdir(full_path):
        file_path = os.path.join(full_path, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    results[filename] = {
                        "content": base64.b64encode(content).decode('utf-8'),
                        "encoding": "base64"
                    }
            except Exception as e:
                results[filename] = {"error": str(e)}
    return {"data": results}

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
            "result": {"protocolVersion": "1.0.0", "serverInfo": {"name": "File Fetch Tool"}}
        })
    elif method == "tools/list":
        tools = [{
            "name": "file_fetcher",
            "title": "File Fetcher",
            "description": "Reads all files from a given directory on the network share.",
            "inputSchema": FileFetchArgs.model_json_schema(),
            "outputSchema": {"type": "object"}
        }]
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": {"tools": tools}})
    elif method == "tools/call":
        tool_name = body["params"]["name"]
        tool_args = body["params"].get("arguments", {})
        if tool_name == "file_fetcher":
            args = FileFetchArgs(**tool_args)
            result = read_directory(args.path)
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        else:
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32601, "message": "Method not found"}}, status_code=404)
    else:
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": None})

# --- FastAPI App ---
app = FastAPI()
app.include_router(router, prefix="/api/v1")
