# Integrating MCP Server with Open-webui

## Prerequisites

- A running instance of the **MCP server**. You can follow the instructions in the [main README.md file](../README.md) to run the server.
- A running instance of **Open-webui**. You can find the installation instructions in the [official Open-webui documentation](https://docs.openwebui.com/).

## Creating a Custom Tool

You can create a custom tool in Open-webui to interact with the MCP server. This will allow the LLM to call the methods of the tool to fetch data from the MCP server and generate reports.

To create a custom tool, you need to create a Python file in the `tools` directory of your Open-webui installation. You can name the file `mcp_tool.py`.

Here is the code for the custom tool:

> ```python
> import os
> import requests
> from pydantic import BaseModel, Field
>
import os
import requests
import json
from pydantic import BaseModel, Field

class Tools:
    def __init__(self):
        self.gateway_url = "http://192.168.1.9:8000/api/v1/mcp" # Gateway endpoint

    def _call_gateway_tool(self, tool_name: str, **kwargs) -> str:
        """Helper to call tools via the gateway."""
        tool_call_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": kwargs,
            },
            "id": "1",
        }
        try:
            response = requests.post(self.gateway_url, json=tool_call_payload)
            response.raise_for_status()
            return response.json().get("result", {})
        except requests.RequestException as e:
            return f"Error calling tool '{tool_name}': {str(e)}"
        except KeyError as e:
            return f"Error parsing gateway response for tool '{tool_name}': Missing key {e}"
        except json.JSONDecodeError as e:
            return f"Error decoding JSON from gateway for tool '{tool_name}': {str(e)}"

    def get_stock_price(self, ticker: str = Field(..., description="The stock ticker symbol, e.g., 'AAPL' for Apple.")) -> str:
        """
        Fetches the current stock price for a given ticker symbol.
        """
        return self._call_gateway_tool("get_stock_price", ticker=ticker)

    def file_fetcher(self, path: str = Field(..., description="The absolute path to the directory to read.")) -> str:
        """
        Reads all files from a given directory and returns their content.
        """
        return self._call_gateway_tool("file_fetcher", path=path)

    def get_weather_forecast(self, lat: float = Field(..., description="The latitude of the location."), lon: float = Field(..., description="The longitude of the location.")) -> str:
        """
        Fetches the current weather for a specified location.
        """
        return self._call_gateway_tool("openweather_get_hourly_forecast", lat=lat, lon=lon)
```

### How to use the tool

Once you have created the custom tool, you can use it in Open-webui by asking the LLM to call the methods of the tool.

For example, you can ask the LLM:

- "What is the stock price of GOOGL?"
- "Read the files in the /data/network_share directory."
- "What is the weather forecast for latitude 40.7128 and longitude -74.0060?"

The LLM will then call the corresponding method of the `Tools` class and return the result.

By following these instructions, you can integrate the MCP server with your Open-webui installation and use it as a powerful tool to fetch data from your internal systems and generate reports.