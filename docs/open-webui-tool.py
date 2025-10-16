
import requests
import json

# Configuration
MCP_SERVER_URL = "http://localhost:8000/api/v1/mcp"

def call_mcp_method(method, params=None):
    """Calls a method on the MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": "1"
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(MCP_SERVER_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # 1. Initialize
    print("1. Initializing MCP Server...")
    init_response = call_mcp_method("initialize")
    print("Response:", json.dumps(init_response, indent=2))

    # 2. List Tools
    print("\n2. Listing available tools...")
    list_response = call_mcp_method("tools/list")
    print("Response:", json.dumps(list_response, indent=2))

    # 3. Call a tool (example: get_stock_price)
    print("\n3. Calling 'get_stock_price' tool...")
    tool_params = {"name": "get_stock_price", "arguments": {"ticker": "AAPL"}}
    call_response = call_mcp_method("tools/call", tool_params)
    print("Response:", json.dumps(call_response, indent=2))
