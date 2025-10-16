
from fastapi import FastAPI, APIRouter, Request
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import os

# --- Pydantic Schemas ---
class GetStockPriceArgs(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol.")

# --- Tool Implementation ---
def get_stock_price(args: GetStockPriceArgs):
    """
    Fetches the current stock price for a given ticker symbol using Alpha Vantage.
    """
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
    if not api_key:
        return "Alpha Vantage API key is not configured."

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={args.ticker}&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price = data["Global Quote"]["05. price"]
            return f"The current stock price of {args.ticker} is {price}"
        else:
            return f"Could not find stock price for {args.ticker}. Response: {data}"
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
            "result": {"protocolVersion": "1.0.0", "serverInfo": {"name": "Yahoo Finance Tool"}}
        })
    elif method == "tools/list":
        tools = [{
            "name": "get_stock_price",
            "title": "Get Stock Price",
            "description": "Fetches the current stock price for a given ticker symbol.",
            "inputSchema": GetStockPriceArgs.model_json_schema(),
            "outputSchema": {"type": "string"}
        }]
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": {"tools": tools}})
    elif method == "tools/call":
        tool_name = body["params"]["name"]
        tool_args = body["params"].get("arguments", {})
        if tool_name == "get_stock_price":
            args = GetStockPriceArgs(**tool_args)
            result = get_stock_price(args)
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        else:
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32601, "message": "Method not found"}}, status_code=404)
    else:
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": None})

# --- FastAPI App ---
app = FastAPI()
app.include_router(router, prefix="/api/v1")
