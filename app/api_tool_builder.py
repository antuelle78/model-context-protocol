import httpx
import json

async def generate_tools_from_openapi(openapi_url: str, api_name: str, auth: httpx.Auth = None) -> list:
    """
    Fetches an OpenAPI specification and generates a list of tool definitions.
    """
    tool_definitions = []
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(openapi_url, auth=auth)
            response.raise_for_status()
            spec = response.json()
            print(f"Successfully parsed OpenAPI spec for {api_name}")

        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method not in ["get", "post", "put", "delete"]:
                    continue

                operation_id = operation.get("operationId")
                if not operation_id:
                    # Create a descriptive name if operationId is missing
                    operation_id = f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}"

                tool_name = f"{api_name}_{operation_id}"
                description = operation.get("summary") or operation.get("description", "")
                
                input_schema = {
                    "type": "object",
                    "properties": {},
                    "required": [],
                }

                for param in operation.get("parameters", []):
                    param_name = param.get("name")
                    param_schema = param.get("schema", {})
                    input_schema["properties"][param_name] = {
                        "type": param_schema.get("type", "string"),
                        "description": param.get("description", ""),
                    }
                    if param.get("required"):
                        input_schema["required"].append(param_name)

                if "requestBody" in operation:
                    request_body = operation["requestBody"]["content"]
                    if "application/json" in request_body:
                        schema = request_body["application/json"]["schema"]
                        # This is a simplification; a real implementation would handle complex schemas
                        if "properties" in schema:
                            for prop_name, prop_schema in schema["properties"].items():
                                input_schema["properties"][prop_name] = {
                                    "type": prop_schema.get("type", "string"),
                                    "description": prop_schema.get("description", ""),
                                }
                                if prop_name in schema.get("required", []):
                                    input_schema["required"].append(prop_name)


                tool_definitions.append({
                    "name": tool_name,
                    "title": tool_name.replace("_", " ").title(),
                    "description": description,
                    "inputSchema": input_schema,
                    "outputSchema": {"type": "object", "properties": {"data": {"type": "object"}}},
                    "annotations": {
                        "path": path,
                        "method": method,
                        "api_name": api_name,
                    },
                })
    except Exception as e:
        print(f"Failed to generate tools from OpenAPI spec at {openapi_url}: {e}")

    return tool_definitions
