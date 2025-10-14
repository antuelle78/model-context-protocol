# Model Context Protocol (MCP) Server

This project implements a RESTful API that serves as the data backbone for ITSM reporting. It fetches ticketing data from ServiceNow and GLPI, and provides tools to generate eye-catching reports in CSV format.

## Features

- **MCP Endpoint** (`POST /api/v1/mcp`): A unified endpoint for all MCP-compliant tools.
- **ServiceNow Integration**: Tools for interacting with ServiceNow.
- **GLPI Integration**: Tools for interacting with a GLPI instance, including a tool to get inventory details.
- **File Tools**: Tools for interacting with the local filesystem.

All endpoints are documented in OpenAPI format and automatically served by FastAPI.

## Architecture

A flowchart depicting the project architecture can be found in the [architecture documentation](docs/architecture.md).

## Project Structure

```text
/home/mnelson-ext/model-context-protocol/
├───.env
├───docker-compose.yml
├───mcp.json
├───README.md
├───requirements.txt
├───swagger.json
├───test.db
├───.git/...
├───app/
│   ├───__init__.py
│   ├───api_tool_builder.py
│   ├───config.py
│   ├───database.py
│   ├───main.py
│   ├───mcp_router.py
│   ├───models.py
│   ├───schemas.py
│   ├───services.py
│   ├───tool_utils.py
│   └───yahoo_finance_tools.py
├───data/
│   ├───jokes.txt
│   ├───poem.txt
│   └───story.txt
├───docker/
│   ├───docker-compose.yml
│   ├───Dockerfile
│   └───integration_instructions.md
├───docs/
│   ├───api_documentation.md
│   ├───architecture.md
│   ├───integration_instructions.md
│   ├───open-webui-tool.py
│   └───README.md
├───file_service/
│   ├───Dockerfile
│   ├───main.py
│   └───requirements.txt
├───glpi_service/
│   ├───config.py
│   ├───database.py
│   ├───Dockerfile
│   ├───glpi_api_service.py
│   ├───main.py
│   ├───models.py
│   ├───requirements.txt
│   └───schemas.py
├───mock_glpi_api/
│   ├───app.py
│   ├───Dockerfile
│   └───requirements.txt
├───mock_servicenow_api/
│   ├───app.py
│   ├───Dockerfile
│   └───requirements.txt
├───network_share/
│   ├───config.json
│   ├───logo.png
│   └───report_data.csv
├───servicenow_service/
│   ├───config.py
│   ├───database.py
│   ├───Dockerfile
│   ├───main.py
│   ├───models.py
│   ├───requirements.txt
│   ├───schemas.py
│   └───services.py
└───tests/
    ├───conftest.py
    └───test_main.py
```

## Setup and Running

1.  **Create a virtual environment:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file** in the root of the project. You can use the `.env.example` file as a template if one is available.

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
    source .venv/bin/activate
    ```

2.  **Run the tests:**

    ```bash
    PYTHONPATH=. .venv/bin/pytest
    ```

## Open-webui Custom Tool

To integrate with Open-webui, you can create a custom tool that interacts with the MCP server. See the `docs/open-webui-tool.py` file for an example.