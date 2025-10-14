import pytest
from fastapi.testclient import TestClient
import respx
import httpx
from app.database import SessionLocal
from app.models import Ticket
import base64
import json

@pytest.fixture(scope="function")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





from unittest.mock import patch, MagicMock

@patch('app.tool_utils.httpx.AsyncClient')
def test_chat_completions_tool_call(mock_async_client, client: TestClient, db_session):


    # Mock httpx.AsyncClient for the microservice call
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"report": "INC009,Ticket 9,Group 1"}
    mock_response.raise_for_status.return_value = None
    mock_async_client.return_value.__aenter__.return_value.post.return_value = mock_response
    mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response


    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_report_open_by_priority",
            "arguments": {"priority": "1 - Critical"},
        },
    }
    response = client.post("/api/v1/mcp", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "result" in data
    assert "INC009,Ticket 9,Group 1" in data["result"]["report"]

def test_chat_completions_initialize(client: TestClient):
    request_data = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "lmstudio-mcp-bridge", "version": "1.0.0"},
        },
    }
    response = client.post("/api/v1/mcp", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 0
    assert "result" in data
    assert "serverInfo" in data["result"]
    assert data["result"]["serverInfo"]["name"] == "MCP Server"