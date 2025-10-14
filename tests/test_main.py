import pytest
from fastapi.testclient import TestClient
import respx
from unittest.mock import patch

# Sample OpenAPI spec for a mock API
mock_openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": "Mock API", "version": "1.0.0"},
    "paths": {
        "/users/{userId}": {
            "get": {
                "operationId": "getUserById",
                "summary": "Get a user by their ID",
                "parameters": [
                    {
                        "name": "userId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "A user object",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "name": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}

# Mock API configuration
from app.config import ApiConfig

mock_api_config = [
    ApiConfig(
        name="mock_api",
        base_url="https://api.mock.com",
        openapi_url="https://api.mock.com/openapi.json",
        auth_type="bearer",
        auth_key="test_token",
    )
]

@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c

@respx.mock
def test_tools_list_dynamic(client: TestClient):
    """
    Tests if the server can dynamically generate tools from a mock OpenAPI spec.
    """
    # Mock the request to fetch the OpenAPI spec
    respx.get(mock_api_config[0].openapi_url).respond(200, json=mock_openapi_spec)

    with patch("app.config.settings.APIs", mock_api_config):
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }
        response = client.post("/api/v1/mcp", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "result" in data
        assert "tools" in data["result"]
        
        tools = data["result"]["tools"]
        # Check if the dynamic tool was generated
        getUserTool = next((t for t in tools if t["name"] == "getUserById"), None)
        assert getUserTool is not None
        assert getUserTool["description"] == "Get a user by their ID"
        assert "userId" in getUserTool["inputSchema"]["properties"]

@respx.mock
def test_tool_call_dynamic(client: TestClient):
    """
    Tests if the server can correctly execute a dynamically generated tool.
    """
    # Mock the request to fetch the OpenAPI spec
    respx.get(mock_api_config[0].openapi_url).respond(200, json=mock_openapi_spec)
    
    # Mock the actual API call that the tool will make
    user_id = 123
    mock_user_response = {"id": user_id, "name": "John Doe"}
    api_call_route = respx.get(f"https://api.mock.com/users/{user_id}")
    api_call_route.respond(200, json=mock_user_response)

    with patch("app.config.settings.APIs", mock_api_config):
        request_data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "getUserById",
                "arguments": {"userId": user_id},
            },
        }
        response = client.post("/api/v1/mcp", json=request_data)
        assert response.status_code == 200
        data = response.json()

        assert "result" in data
        assert data["result"] == mock_user_response
        assert api_call_route.called
        
        # Verify that the correct auth header was sent
        sent_headers = api_call_route.calls.last.request.headers
        assert "authorization" in sent_headers
        assert sent_headers["authorization"] == f"Bearer {mock_api_config[0].auth_key}"

@respx.mock
def test_get_hourly_forecast(client: TestClient):
    """
    Tests the get_hourly_forecast tool.
    """
    lat = 34.05
    lon = -118.24
    api_key = "test_api_key"
    mock_forecast_response = {"city": {"name": "Los Angeles"}, "list": [{"dt_txt": "2025-10-14 12:00:00", "main": {"temp": 290.15}}]}
    
    forecast_url = f"https://pro.openweathermap.org/data/2.5/forecast/hourly?lat={lat}&lon={lon}&appid={api_key}"
    forecast_route = respx.get(forecast_url)
    forecast_route.respond(200, json=mock_forecast_response)

    with patch("app.config.settings.OPENWEATHER_API_KEY", api_key):
        request_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_hourly_forecast",
                "arguments": {"lat": lat, "lon": lon},
            },
        }
        response = client.post("/api/v1/mcp", json=request_data)
        assert response.status_code == 200
        data = response.json()

        assert "result" in data
        assert data["result"] == mock_forecast_response
        assert forecast_route.called
