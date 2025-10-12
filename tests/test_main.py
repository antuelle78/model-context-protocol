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

@patch('app.main.httpx.AsyncClient')
def test_chat_completions_tool_call(mock_async_client, client: TestClient, db_session):


    # Mock httpx.AsyncClient for the microservice call
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"report": "INC009,Ticket 9,Group 1"}
    mock_response.raise_for_status.return_value = None
    mock_async_client.return_value.__aenter__.return_value.post.return_value = mock_response
    mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response


    request_data = {
        "messages": [
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "name": "get_report_open_by_priority",
                        "arguments": {"priority": "1 - Critical"},
                    }
                ),
            }
        ],
        "model": "gpt-3.5-turbo",
    }
    response = client.post("/api/v1/chat/completions", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "INC009,Ticket 9,Group 1" in data["choices"][0]["message"]["content"]

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
    response = client.post("/api/v1/chat/completions", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 0
    assert "result" in data
    assert "serverInfo" in data["result"]
    assert data["result"]["serverInfo"]["name"] == "MCP Server"