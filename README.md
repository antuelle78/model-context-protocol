# Model Context Protocol (MCP) Server

This project implements a RESTful API that serves as the data backbone for ITSM reporting. It fetches ticketing data from ServiceNow and GLPI, and provides tools to generate eye-catching reports in CSV format.

## Features

- **Fetch Tickets** (`POST /api/v1/tickets/fetch`): Fetches the latest tickets from ServiceNow and stores them in the database.
- **Generate Reports** (`GET /api/v1/reports/{report_type}`): Generates various CSV reports based on ticketing data.
  - `open_by_priority`: Report of open tickets by priority.
  - `by_assignment_group`: Report of tickets by assignment group.
  - `recently_resolved`: Report of recently resolved tickets.
- **OpenAI Compatible Endpoint** (`POST /api/v1/chat/completions`): Allows integration with OpenAI-compatible clients (e.g., LM Studio) to interact with the reporting tools.
- **GLPI Integration**: Provides tools to interact with a GLPI instance.
  - `get_glpi_laptop_count`: Returns the number of laptops in GLPI.
  - `get_glpi_pc_count`: Returns the number of PCs (desktop computers) in GLPI.
  - `get_glpi_monitor_count`: Returns the number of monitors in GLPI.
  - `get_glpi_os_distribution`: Returns a breakdown of operating system usage across computers in GLPI.
  - `get_glpi_full_asset_dump`: Returns a complete dump of all assets of a specified type from GLPI.

All endpoints are documented in OpenAPI format and automatically served by FastAPI.

## Architecture

A flowchart depicting the project architecture can be found in the [architecture documentation](docs/architecture.md).

## Project Structure

```text
/home/ghost/bin/docker/model-context-protocol/
├───.gitignore
├───requirements.txt
├───app/
│   ├───__init__.py
│   ├───config.py
│   ├───database.py
│   ├───main.py
│   ├───models.py
│   ├───schemas.py
│   ├───services.py
│   └───tools.py
├───docker/
│   ├───docker-compose.yml
│   ├───Dockerfile
│   └───integration_instructions.md
├───docs/
│   ├───api_documentation.md
│   ├───architecture.md
│   ├───integration_instructions.md
│   └───README.md
├───tests/
│   ├───conftest.py
│   └───test_main.py
└───mcp.json
```

## Setup and Running

1.  **Create a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file** in the root of the project. You can use the `.env.example` file as a template:

    ```bash
    cp .env.example .env
    ```

4.  **Run the application:**

    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

## Running with Docker

1.  **Create a `.env` file** in the root of the project. You can use the `.env.example` file as a template:

    ```bash
    cp .env.example .env
    ```

2.  **Build and run the container:**

    ```bash
    docker-compose -f docker/docker-compose.yml up -d --build
    ```

## Running the tests

1.  **Activate the virtual environment:**

    ```bash
    source venv/bin/activate
    ```

2.  **Run the tests:**

    ```bash
    pytest
    ```

## LM Studio Integration

To integrate with LM Studio, you need to provide an `mcp.json` file that describes the MCP server and its tools.

1.  **Create an `mcp.json` file** in the LM Studio plugins directory (or a location where LM Studio can find it) with the following content:

    ```json
    {
      "mcpServers": {
        "MCP Server": {
          "url": "http://localhost:8000/api/v1/chat/completions",
          "tools": [
            {
              "type": "function",
              "function": {
                "name": "fetch_all_servicenow_tickets",
                "description": "Fetches the latest tickets from the ITSM and stores them in the database.",
                "parameters": {
                  "type": "object",
                  "properties": {}
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "fetch_all_glpi_inventory",
                "description": "Fetches all inventory from GLPI.",
                "parameters": {
                  "type": "object",
                  "properties": {}
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "get_report_open_by_priority",
                "description": "Generates a CSV report of open tickets by priority.",
                "parameters": {
                  "type": "object",
                  "properties": {
                    "priority": {
                      "type": "string",
                      "description": "The priority of the tickets to include in the report."
                    }
                  },
                  "required": ["priority"]
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "get_report_by_assignment_group",
                "description": "Generates a CSV report of tickets by assignment group.",
                "parameters": {
                  "type": "object",
                  "properties": {
                    "group": {
                      "type": "string",
                      "description": "The assignment group of the tickets to include in the report."
                    }
                  },
                  "required": ["group"]
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "get_report_recently_resolved",
                "description": "Generates a CSV report of recently resolved tickets.",
                "parameters": {
                  "type": "object",
                  "properties": {}
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "get_glpi_laptop_count",
                "description": "Returns the number of laptops in GLPI.",
                "parameters": {
                  "type": "object",
                  "properties": {}
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "get_glpi_pc_count",
                "description": "Returns the number of PCs (desktop computers) in GLPI.",
                "parameters": {
                  "type": "object",
                  "properties": {}
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "get_glpi_monitor_count",
                "description": "Returns the number of monitors in GLPI.",
                "parameters": {
                  "type": "object",
                  "properties": {}
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "get_glpi_os_distribution",
                "description": "Returns a breakdown of operating system usage across computers in GLPI.",
                "parameters": {
                  "type": "object",
                  "properties": {}
                }
              }
            },
            {
              "type": "function",
              "function": {
                "name": "get_glpi_full_asset_dump",
                "description": "Returns a complete dump of all assets of a specified type from GLPI.",
                "parameters": {
                  "type": "object",
                  "properties": {
                    "itemtype": {
                      "type": "string",
                      "description": "The type of asset to dump (e.g., Computer, Monitor)."
                    }
                  },
                  "required": ["itemtype"]
                }
              }
            }
          ]
        }
      }
    }
    ```

2.  **Restart LM Studio** for the changes to take effect.

## Open-webui Custom Tool

To integrate with Open-webui, you can create a custom tool that interacts with the MCP server.

1.  **Create a Python file** (e.g., `mcp_tool.py`) in the `tools` directory of your Open-webui installation.

2.  **Add the following code** to the `mcp_tool.py` file:

    ```python
    import os
    import requests
    from pydantic import BaseModel, Field

    class Tools:
        def __init__(self):
            self.backend_url = "http://localhost:8000" # Or the IP address of your MCP server

        def fetch_all_servicenow_tickets(self) -> str:
            """
            Fetches the latest tickets from the ITSM and stores them in the database.
            """
            try:
                response = requests.post(f"{self.backend_url}/api/v1/chat/completions", json={"method": "tools/call", "params": {"name": "fetch_all_servicenow_tickets", "arguments": {}}})
                response.raise_for_status()
                return response.json()["result"]
            except requests.RequestException as e:
                return f"Error fetching tickets: {str(e)}"

        def fetch_all_glpi_inventory(self) -> str:
            """
            Fetches all inventory from GLPI.
            """
            try:
                response = requests.post(f"{self.backend_url}/api/v1/chat/completions", json={"method": "tools/call", "params": {"name": "fetch_all_glpi_inventory", "arguments": {}}})
                response.raise_for_status()
                return response.json()["result"]
            except requests.RequestException as e:
                return f"Error fetching inventory: {str(e)}"\n\n        def get_report_open_by_priority(self, priority: str = Field(..., description=\"The priority of the tickets to include in the report.\")) -> str:\n            \'\'\'\n            Generates a CSV report of open tickets by priority.\n            \'\'\'\n            try:\n                response = requests.get(f\"{self.backend_url}/api/v1/reports/open_by_priority?priority={priority}\")\n                response.raise_for_status()\n                return response.text\n            except requests.RequestException as e:\n                return f\"Error generating report: {str(e)}\"\n\n        def get_report_by_assignment_group(self, group: str = Field(..., description=\"The assignment group of the tickets to include in the report.\")) -> str:\n            \'\'\'\n            Generates a CSV report of tickets by assignment group.\n            \'\'\'\n            try:\n                response = requests.get(f\"{self.backend_url}/api/v1/reports/by_assignment_group?group={group}\")\n                response.raise_for_status()\n                return response.text\n            except requests.RequestException as e:\n                return f\"Error generating report: {str(e)}\"\n\n        def get_report_recently_resolved(self) -> str:\n            \'\'\'\n            Generates a CSV report of recently resolved tickets.\n            \'\'\'\n            try:\n                response = requests.get(f\"{self.backend_url}/api/v1/reports/recently_resolved\")\n                response.raise_for_status()\n                return response.text\n            except requests.RequestException as e:\n                return f\"Error generating report: {str(e)}\"\n\n        def get_glpi_laptop_count(self) -> str:\n            \'\'\'\n            Returns the number of laptops in GLPI.\n            \'\'\'\n            try:\n                response = requests.get(f\"{self.backend_url}/api/v1/glpi/laptop_count\")\n                response.raise_for_status()\n                return response.json()[\"count\"]\n            except requests.RequestException as e:\n                return f\"Error fetching laptop count: {str(e)}\"\n\n        def get_glpi_pc_count(self) -> str:\n            \'\'\'\n            Returns the number of PCs (desktop computers) in GLPI.\n            \'\'\'\n            try:\n                response = requests.get(f\"{self.backend_url}/api/v1/glpi/pc_count\")\n                response.raise_for_status()\n                return response.json()[\"count\"]\n            except requests.RequestException as e:\n                return f\"Error fetching PC count: {str(e)}\"\n\n        def get_glpi_monitor_count(self) -> str:\n            \'\'\'\n            Returns the number of monitors in GLPI.\n            \'\'\'\n            try:\n                response = requests.get(f\"{self.backend_url}/api/v1/glpi/monitor_count\")\n                response.raise_for_status()\n                return response.json()[\"count\"]\n            except requests.RequestException as e:\n                return f\"Error fetching monitor count: {str(e)}\"\n\n        def get_glpi_os_distribution(self) -> str:\n            \'\'\'\n            Returns a breakdown of operating system usage across computers in GLPI.\n            \'\'\'\            try:\n                response = requests.get(f\"{self.backend_url}/api/v1/glpi/os_distribution\")\n                response.raise_for_status()\n                return response.json()[\"report\"]\n            except requests.RequestException as e:\n                return f\"Error fetching OS distribution: {str(e)}\"\n\n        def get_glpi_full_asset_dump(self, itemtype: str = Field(..., description=\"The type of asset to dump (e.g., Computer, Monitor).\")) -> str:\n            \'\'\'\n            Returns a complete dump of all assets of a specified type from GLPI.\n            \'\'\'\n            try:\n                response = requests.get(f\"{self.backend_url}/api/v1/glpi/full_asset_dump?itemtype={itemtype}\")\n                response.raise_for_status()\n                return response.json()[\"assets\"]\n            except requests.RequestException as e:\n                return f\"Error fetching full asset dump: {str(e)}\"
