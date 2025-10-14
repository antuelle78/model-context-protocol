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
        self.gateway_url = "http://192.168.1.9:8000/api/v1/chat/completions" # Gateway endpoint

    def _call_gateway_tool(self, tool_name: str, **kwargs) -> str:
        """Helper to call tools via the gateway."""
        tool_call_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps({
                        "name": tool_name,
                        "arguments": kwargs
                    })
                }
            ],
            "model": "tool-calling-model" # Placeholder, adjust if needed
        }
        try:
            response = requests.post(self.gateway_url, json=tool_call_payload)
            response.raise_for_status()
            # The gateway returns a ChatCompletionResponse, extract the content
            return response.json()["choices"][0]["message"]["content"]
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

    def file_fetcher(self, path: str = Field(..., description="The absolute path to the directory to read.")) -> str:
        """
        Reads all files from a given directory and returns their content.
        """
        return self._call_gateway_tool("file_fetcher", path=path) ```

### How to use the tool

Once you have created the custom tool, you can use it in Open-webui by asking the LLM to call the methods of the tool.

For example, you can ask the LLM:

- "Fetch the latest tickets"
- "Generate a report of open tickets with priority 1 - Critical"
- "Generate a report of tickets assigned to Group 1"
- "Generate a report of recently resolved tickets"

The LLM will then call the corresponding method of the `Tools` class and return the result.

By following these instructions, you can integrate the MCP server with your Open-webui installation and use it as a powerful tool to fetch data from your internal systems and generate reports.