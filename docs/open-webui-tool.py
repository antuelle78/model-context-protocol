import os
import requests
import json
from pydantic import BaseModel, Field

class Tools:
    def __init__(self):
        self.gateway_url = "http://localhost:8000/api/v1/chat/completions" # Gateway endpoint

    def _call_gateway_tool(self, tool_name: str, **kwargs) -> str:
        """Helper to call tools via the gateway."""
        tool_call_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": kwargs
            },
            "id": 1
        }
        try:
            response = requests.post(self.gateway_url, json=tool_call_payload)
            response.raise_for_status()
            return response.json()["result"]
        except requests.RequestException as e:
            return f"Error calling tool '{tool_name}': {str(e)}"
        except KeyError as e:
            return f"Error parsing gateway response for tool '{tool_name}': Missing key {e}"
        except json.JSONDecodeError as e:
            return f"Error decoding JSON from gateway for tool '{tool_name}': {str(e)}"

    def fetch_all_servicenow_tickets(self) -> str:
        """
        Fetches the latest tickets from ServiceNow and stores them in the database.
        """
        return self._call_gateway_tool("fetch_all_servicenow_tickets")

    def fetch_all_glpi_inventory(self) -> str:
        """
        Fetches all inventory from GLPI.
        """
        return self._call_gateway_tool("fetch_all_glpi_inventory")

    def get_report_open_by_priority(self, priority: str = Field(..., description="The priority of the tickets to include in the report.")) -> str:
        """
        Generates a CSV report of open tickets by priority.
        """
        return self._call_gateway_tool("get_report_open_by_priority", priority=priority)

    def get_report_by_assignment_group(self, group: str = Field(..., description="The assignment group of the tickets to include in the report.")) -> str:
        """
        Generates a CSV report of tickets by assignment group.
        """
        return self._call_gateway_tool("get_report_by_assignment_group", group=group)

    def get_report_recently_resolved(self) -> str:
        """
        Generates a CSV report of recently resolved tickets.
        """
        return self._call_gateway_tool("get_report_recently_resolved")

    def get_glpi_laptop_count(self) -> str:
        """
        Returns the number of laptops in GLPI.
        """
        return self._call_gateway_tool("get_glpi_laptop_count")

    def get_glpi_pc_count(self) -> str:
        """
        Returns the number of PCs (desktop computers) in GLPI.
        """
        return self._call_gateway_tool("get_glpi_pc_count")

    def get_glpi_monitor_count(self) -> str:
        """
        Returns the number of monitors in GLPI.
        """
        return self._call_gateway_tool("get_glpi_monitor_count")

    def get_glpi_os_distribution(self) -> str:
        """
        Returns a breakdown of operating system usage across computers in GLPI.
        """
        return self._call_gateway_tool("get_glpi_os_distribution")

    def get_glpi_full_asset_dump(self, itemtype: str = Field(..., description="The type of assets to dump (e.g., 'Computer', 'Monitor').")) -> str:
        """
        Returns a complete dump of all assets of a specified type from GLPI.
        """
        return self._call_gateway_tool("get_glpi_full_asset_dump", itemtype=itemtype)

    def create_new_ticket(self, short_description: str = Field(..., description="A brief description of the ticket."), assignment_group: str = Field(..., description="The group responsible for resolving the ticket."), priority: str = Field(..., description="The priority of the ticket (e.g., '1 - Critical', '2 - High').")) -> str:
        """
        Creates a new ticket in the ITSM system.
        """
        return self._call_gateway_tool("create_new_ticket", short_description=short_description, assignment_group=assignment_group, priority=priority)