# Grafana MCP Tool 🤖

![Python Version](https://img.shields.io/badge/python-3.9-blue.svg)
![Docker](https://img.shields.io/badge/docker-20.10-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.68-blue.svg)
![Pydantic](https://img.shields.io/badge/pydantic-1.8-blue.svg)
![Requests](https://img.shields.io/badge/requests-2.25-blue.svg)
![Pyzabbix](https://img.shields.io/badge/pyzabbix-1.3-blue.svg)

A powerful MCP server for managing Grafana dashboards and validating Zabbix queries.

## 🚀 Features

*   **Create Grafana Dashboards:** Programmatically create Grafana dashboards from a JSON definition.
*   **Delete Grafana Dashboards:** Delete Grafana dashboards by their UID.
*   **Validate Zabbix Queries:** Check if Zabbix queries are valid before creating the dashboard.
*   **Get Zabbix Data:** Get a list of host groups and hosts from Zabbix.
*   **MCP Compliant:** Fully compliant with the Model Context Protocol.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/grafana_tool.git
    cd grafana_tool
    ```
2.  **Create a `.env` file:**
    Create a `.env` file in the root of the project and add the following environment variables:
    ```
    GRAFANA_URL=https://your-grafana-url.com
    GRAFANA_API_TOKEN=your-grafana-api-token
    ZABBIX_URL=http://your-zabbix-url/api_jsonrpc.php
    ZABBIX_USER=your-zabbix-user
    ZABBIX_PASSWORD=your-zabbix-password
    ```
3.  **Build and run the Docker container:**
    ```bash
    docker-compose build
    docker-compose up -d
    ```

## Usage

The `grafana_tool` server exposes an MCP endpoint at `http://localhost:8003/api/v1/mcp`.
You can interact with the tools by sending a POST request to this endpoint.

### Example: Create a dashboard

```json
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
        "name": "create_grafana_dashboard",
        "arguments": {
            "dashboard_json": {
                "title": "My Dashboard",
                "panels": [
                    {
                        "title": "My Panel",
                        "type": "graph",
                        "datasource": "zabbix",
                        "targets": [
                            {
                                "item": {
                                    "filter": "system.cpu.load[percpu,avg1]"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

## API Reference

### `create_grafana_dashboard`

Creates a new Grafana dashboard from a JSON definition.

**Arguments:**

*   `dashboard_json` (dict): The JSON definition of the Grafana dashboard.

### `delete_grafana_dashboard`

Deletes a Grafana dashboard.

**Arguments:**

*   `uid` (str): The UID of the dashboard to delete.

### `check_zabbix_query`

Checks if a Zabbix query is valid.

**Arguments:**

*   `query` (dict): The Zabbix query to check.
*   `host` (str): The host to execute the query on.
*   `group` (str): The group to execute the query on.

### `get_zabbix_data`

Gets a list of host groups and hosts from Zabbix.

**Arguments:**

*   None
