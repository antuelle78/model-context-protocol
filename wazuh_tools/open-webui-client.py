"""
title: 'Wazuh Tools'
author: 'Gemini'
description: 'A set of tools to interact with the Wazuh API.'
version: '1.0.0'
requirements: httpx
"""

import httpx
import json


class Tools:
    def __init__(self):
        # IMPORTANT: Replace with the actual IP of the machine running the MCP server
        self.mcp_server_url = "http://<NODE_IP>:30085/api/v1/mcp"
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
                response = client.post(
                    self.mcp_server_url, json=payload, headers=self.headers
                )
                response.raise_for_status()
                result = response.json().get("result", {})
                return json.dumps(result, indent=2)
        except httpx.HTTPStatusError as e:
            return f"Error: The tool server returned a status of {e.response.status_code}. Response: {e.response.text}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    async def get_agents(self, **kwargs) -> str:
        """Gets a list of all Wazuh agents."""
        return self._call_mcp_tool("get_agents", **kwargs)

    async def get_agent_details(self, agent_id: str) -> str:
        """Gets the details of a specific Wazuh agent."""
        return self._call_mcp_tool("get_agent_details", agent_id=agent_id)

    async def get_rules(self, **kwargs) -> str:
        """Gets a list of all Wazuh rules."""
        return self._call_mcp_tool("get_rules", **kwargs)

    async def get_alerts(self, **kwargs) -> str:
        """Gets a list of all Wazuh alerts."""
        return self._call_mcp_tool("get_alerts", **kwargs)

    async def add_agent(self, name: str, ip: str = None) -> str:
        """Adds a new agent."""
        return self._call_mcp_tool("add_agent", name=name, ip=ip)

    async def delete_agents(self, **kwargs) -> str:
        """Deletes one or more agents."""
        return self._call_mcp_tool("delete_agents", **kwargs)

    async def restart_agents(self, **kwargs) -> str:
        """Restarts one or more agents."""
        return self._call_mcp_tool("restart_agents", **kwargs)

    async def get_agent_key(self, agent_id: str) -> str:
        """Returns the key of an agent."""
        return self._call_mcp_tool("get_agent_key", agent_id=agent_id)

    async def get_vulnerabilities(self, agent_id: str, **kwargs) -> str:
        """Gets the vulnerabilities of a specific agent."""
        return self._call_mcp_tool("get_vulnerabilities", agent_id=agent_id, **kwargs)
