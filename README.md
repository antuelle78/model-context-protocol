# Model Context Protocol (MCP) Server

This project implements a RESTful API that serves as the data backbone for ITSM reporting. It fetches ticketing data from ServiceNow and GLPI, and provides tools to generate eye-catching reports in CSV format.

## Features

- **MCP Endpoint** (`POST /api/v1/mcp`): A unified endpoint for all MCP-compliant tools.
- **ServiceNow Integration**: Tools for interacting with ServiceNow.
- **GLPI Integration**: Tools for interacting with a GLPI instance.
- **File Tools**: Tools for interacting with the local filesystem.

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
│   └───services.py
├───docker/
│   ├───docker-compose.yml
│   └───Dockerfile
├───docs/
│   ├───api_documentation.md
│   ├───architecture.md
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

## Configuration

The application is configured using a `.env` file in the project root. The `APIs` variable is a JSON string that defines the APIs to connect to.

```
DB_URL="sqlite:///./test.db"
APIs='[
  {
    "name": "servicenow",
    "base_url": "https://your-instance.service-now.com",
    "openapi_url": "https://your-instance.service-now.com/api/now/api-doc",
    "auth_type": "basic",
    "auth_user": "your-username",
    "auth_pass": "your-password"
  },
  {
    "name": "glpi",
    "base_url": "https://your-glpi-instance.com/apirest.php",
    "openapi_url": "https://your-glpi-instance.com/apirest.php/openapi.json",
    "auth_type": "bearer",
    "auth_key": "your-glpi-user-token"
  }
]'
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

## Network Share Integration

To allow the `file_fetcher` tool to access files from a network share, you need to mount the share to a local directory and then mount that directory into the `mcp-server` container.

1.  **Mount your network share** to a directory on your host machine. For example:
    ```bash
    mkdir -p /mnt/my_network_share
    mount -t cifs //server/share /mnt/my_network_share -o username=user,password=pass
    ```

2.  **Update the `docker-compose.yml`** file to mount the local directory into the container. Add the following to the `mcp-server` service definition:
    ```yaml
    volumes:
      - /mnt/my_network_share:/data/network_share
    ```

3.  **Use the `file_fetcher` tool** by providing a path relative to the root of the network share. For example, to list the files in the root of the share, you would use:
    ```json
    {
      "name": "file_fetcher",
      "arguments": {
        "path": "."
      }
    }
    ```

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
