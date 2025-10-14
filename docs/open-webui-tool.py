"""
title: 'MCP Bridge'
author: 'MCP Server'
description: 'A bridge to connect to a generic MCP server for executing dynamic tools.'
version: '1.0.0'
requirements: httpx
"""

import httpx
import json

class Tools:
    def __init__(self):
        # IMPORTANT: Replace with the actual IP of the machine running the MCP server
        self.mcp_server_url = "http://10.2.0.150:30080/api/v1/mcp"
        self.headers = {"Content-Type": "application/json"}

    def _call_mcp_tool(self, tool_name: str, **kwargs) -> str:
        """Helper function to call a tool on the MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": kwargs,
            },
            "id": "1",
        }
        try:
            with httpx.Client() as client:
                response = client.post(self.mcp_server_url, json=payload, headers=self.headers)
                response.raise_for_status()
                result = response.json().get("result", {})
                return json.dumps(result, indent=2)
        except httpx.HTTPStatusError as e:
            return f"Error: The tool server returned a status of {e.response.status_code}. Response: {e.response.text}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    async def file_fetcher(self, path: str) -> str:
        """
        Reads all files from a given directory on the network share.

        :param path: The path to the directory on the network share, relative to the root.
        :return: A JSON string containing the file contents and their encodings.
        """
        return self._call_mcp_tool("file_fetcher", path=path)

    async def openweather_get_hourly_forecast(self, lat: float, lon: float) -> str:
        """
        Gets the hourly weather forecast for a given location using the OpenWeather API.

        :param lat: The latitude of the location.
        :param lon: The longitude of the location.
        :return: A JSON string containing the hourly weather forecast.
        """
        return self._call_mcp_tool("openweather_get_hourly_forecast", lat=lat, lon=lon)

    async def get_stock_price(self, ticker: str) -> str:
        """
        Fetches the current stock price for a given ticker symbol.

        :param ticker: The stock ticker symbol, e.g., 'AAPL' for Apple.
        :return: A JSON string containing the stock price.
        """
        return self._call_mcp_tool("get_stock_price", ticker=ticker)

    async def glpi_get_inventory_details(self) -> str:
        """
        Fetches a detailed list of all inventory items from GLPI.

        :return: A JSON string containing the inventory details.
        """
        return self._call_mcp_tool("glpi_get_inventory_details")

    # You can add more static definitions here for other dynamically generated tools
    # that you want to explicitly expose to Open-WebUI.
