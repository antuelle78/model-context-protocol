from app.config import settings
import httpx
import os
import base64

def read_directory(path: str):
    """
    Reads all files from a given directory on the network share and returns their content.
    Text files are returned as strings, and binary files are returned as Base64-encoded strings.
    The path is relative to the root of the network share.
    """
    base_path = "/data/network_share"
    # Security check to prevent directory traversal
    full_path = os.path.abspath(os.path.join(base_path, path))
    if not full_path.startswith(os.path.abspath(base_path)):
        raise ValueError("Access denied: Path is outside the network share.")

    if not os.path.isdir(full_path):
        raise ValueError("Invalid directory path")

    file_contents = {}
    for filename in os.listdir(full_path):
        filepath = os.path.join(full_path, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                file_contents[filename] = {
                    "encoding": "utf-8",
                    "content": content,
                }
            except UnicodeDecodeError:
                with open(filepath, "rb") as f:
                    content = f.read()
                file_contents[filename] = {
                    "encoding": "base64",
                    "content": base64.b64encode(content).decode("utf-8"),
                }
            except Exception as e:
                file_contents[filename] = {
                    "encoding": "error",
                    "content": str(e),
                }

    return file_contents

async def get_weather_forecast(lat: float, lon: float):
    """
    Fetches the current weather for a specified location.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API request failed with status {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}

async def execute_dynamic_api_tool(base_url: str, path: str, method: str, auth: httpx.Auth, headers: dict, tool_args: dict):
    """
    Executes a dynamically generated API tool.
    """
    url = f"{base_url}{path}"
    print(f"Calling API URL: {url}")
    
    # Replace path parameters
    for key, value in tool_args.items():
        if f"{{{key}}}" in url:
            url = url.replace(f"{{{key}}}", str(value))

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                auth=auth,
                headers=headers,
                json=tool_args, # Simplified for now
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API request failed with status {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
