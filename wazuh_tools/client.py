import requests
import json

# The URL of the Wazuh Tools API
url = "http://<NODE_IP>:30085/api/v1/mcp"

# Replace <NODE_IP> with the IP address of your k3s cluster node

# --- Get the list of tools ---
def get_tools():
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/list",
        "params": {}
    }
    response = requests.post(url, json=payload)
    print(response.json())

# --- Get the list of agents ---
def get_agents():
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {
            "name": "get_agents",
            "arguments": {
                "status": "active"
            }
        }
    }
    response = requests.post(url, json=payload)
    print(response.json())

if __name__ == "__main__":
    print("--- Getting the list of tools ---")
    get_tools()
    print("\n--- Getting the list of active agents ---")
    get_agents()

