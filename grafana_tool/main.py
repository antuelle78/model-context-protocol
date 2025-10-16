from fastapi import FastAPI, APIRouter, Request
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import os
import json
from pyzabbix import ZabbixAPI

# --- Pydantic Schemas ---
class CreateDashboardArgs(BaseModel):
    dashboard_json: dict = Field(..., description="The JSON definition of the Grafana dashboard.")

class DeleteDashboardArgs(BaseModel):
    uid: str = Field(..., description="The UID of the dashboard to delete.")

class SearchDashboardsArgs(BaseModel):
    query: str = Field(..., description="The search query to find dashboards by title or other metadata.")

class GetDashboardByUidArgs(BaseModel):
    uid: str = Field(..., description="The UID of the dashboard to retrieve.")

class ListTeamsArgs(BaseModel):
    query: str = Field(None, description="Optional: A search query to filter teams by name.")
    page: int = Field(1, description="Optional: Page number for pagination.")
    per_page: int = Field(1000, description="Optional: Number of teams per page.")

class ListUsersArgs(BaseModel):
    query: str = Field(None, description="Optional: A search query to filter users by login, email, or name.")
    page: int = Field(1, description="Optional: Page number for pagination.")
    per_page: int = Field(1000, description="Optional: Number of users per page.")

class CheckZabbixQueryArgs(BaseModel):
    query: dict = Field(..., description="The Zabbix query to check.")
    host: str = Field(..., description="The host to execute the query on.")
    group: str = Field(..., description="The group to execute the query on.")

class GetZabbixDataArgs(BaseModel):
    pass

# --- Tool Implementation ---
def create_grafana_dashboard(args: CreateDashboardArgs):
    """
    Creates a new Grafana dashboard from a JSON definition.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return {"error": "Grafana URL or API token is not configured."}

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }
    
    # Ensure the dashboard JSON is correctly formatted
    payload = {
        "dashboard": args.dashboard_json,
        "overwrite": True
    }

    try:
        response = requests.post(f"{grafana_url}/api/dashboards/db", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}

def delete_grafana_dashboard(args: DeleteDashboardArgs):
    """
    Deletes a Grafana dashboard.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    try:
        response = requests.delete(f"{grafana_url}/api/dashboards/uid/{args.uid}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def search_grafana_dashboards(args: SearchDashboardsArgs):
    """
    Searches for Grafana dashboards by title or other metadata.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    try:
        response = requests.get(f"{grafana_url}/api/search?query={args.query}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def get_grafana_dashboard_by_uid(args: GetDashboardByUidArgs):
    """
    Retrieves a Grafana dashboard by its UID.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    try:
        response = requests.get(f"{grafana_url}/api/dashboards/uid/{args.uid}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def list_grafana_teams(args: ListTeamsArgs):
    """
    Lists all teams in Grafana.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    params = {
        "query": args.query,
        "page": args.page,
        "perpage": args.per_page
    }

    try:
        response = requests.get(f"{grafana_url}/api/teams/search", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def list_grafana_users(args: ListUsersArgs):
    """
    Lists all users in a Grafana organization.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    params = {
        "query": args.query,
        "page": args.page,
        "perpage": args.per_page
    }

    try:
        response = requests.get(f"{grafana_url}/api/users", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def check_zabbix_query(args: CheckZabbixQueryArgs):
    """
    Lists all users in a Grafana organization.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    params = {
        "query": args.query,
        "page": args.page,
        "perpage": args.per_page
    }

    try:
        response = requests.get(f"{grafana_url}/api/users", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

    """
    Lists all teams in Grafana.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    params = {
        "query": args.query,
        "page": args.page,
        "perpage": args.per_page
    }

    try:
        response = requests.get(f"{grafana_url}/api/teams/search", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

    """
    Retrieves a Grafana dashboard by its UID.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    try:
        response = requests.get(f"{grafana_url}/api/dashboards/uid/{args.uid}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

    """
    Deletes a Grafana dashboard.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    api_token = os.environ.get("GRAFANA_API_TOKEN")

    if not grafana_url or not api_token:
        return "Grafana URL or API token is not configured."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "x-grafana-org-id": "1"
    }

    try:
        response = requests.delete(f"{grafana_url}/api/dashboards/uid/{args.uid}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def check_zabbix_query(args: CheckZabbixQueryArgs):
    """
    Checks if a Zabbix query is valid.
    """
    zabbix_url = os.environ.get("ZABBIX_URL")
    zabbix_user = os.environ.get("ZABBIX_USER")
    zabbix_password = os.environ.get("ZABBIX_PASSWORD")

    if not zabbix_url or not zabbix_user or not zabbix_password:
        return {"success": False, "error_message": "Zabbix credentials are not configured."}

    try:
        zapi = ZabbixAPI(zabbix_url)
        zapi.login(zabbix_user, zabbix_password)
        
        # Replace template variables
        query_str = json.dumps(args.query)
        query_str = query_str.replace("$Group", args.group)
        query_str = query_str.replace("$Host", args.host)
        query = json.loads(query_str)

        items = zapi.item.get(groupids=zapi.hostgroup.get(filter={"name": [args.group]})[0]["groupid"], hostids=zapi.host.get(filter={"host": [args.host]})[0]["hostid"], filter={"name": query["item"]["filter"]}, output=["name"])
        if items:
            return {"success": True, "data": items}
        else:
            return {"success": False, "error_message": f"No item found with query: {query['item']['filter']}"}
    except Exception as e:
        return {"success": False, "error_message": str(e)}


def get_zabbix_data(args: GetZabbixDataArgs):
    """
    Gets a list of host groups and hosts from Zabbix.
    """
    zabbix_url = os.environ.get("ZABBIX_URL")
    zabbix_user = os.environ.get("ZABBIX_USER")
    zabbix_password = os.environ.get("ZABBIX_PASSWORD")

    if not zabbix_url or not zabbix_user or not zabbix_password:
        return {"success": False, "error_message": "Zabbix credentials are not configured."}

    try:
        zapi = ZabbixAPI(zabbix_url)
        zapi.login(zabbix_user, zabbix_password)
        host_groups = [group["name"] for group in zapi.hostgroup.get(output=["name"])]
        hosts = [host["host"] for host in zapi.host.get(output=["host"])]
        return {"host_groups": host_groups, "hosts": hosts}
    except Exception as e:
        return {"success": False, "error_message": str(e)}


# --- MCP Router ---
router = APIRouter()

@router.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method")
    id = body.get("id")

    if method == "initialize":
        return JSONResponse(content={
            "jsonrpc": "2.0", "id": id,
            "result": {"protocolVersion": "1.0.0", "serverInfo": {"name": "Grafana Tool"}}
        })
    elif method == "tools/list":
        tools = [
            {
                "name": "create_grafana_dashboard",
                "title": "Create Grafana Dashboard",
                "description": "Creates a new Grafana dashboard from a JSON definition. The `dashboard_json` should be a complete Grafana dashboard model.",
                "inputSchema": CreateDashboardArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "delete_grafana_dashboard",
                "title": "Delete Grafana Dashboard",
                "description": "Deletes a Grafana dashboard.",
                "inputSchema": DeleteDashboardArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "search_grafana_dashboards",
                "title": "Search Grafana Dashboards",
                "description": "Searches for Grafana dashboards by title or other metadata.",
                "inputSchema": SearchDashboardsArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "get_grafana_dashboard_by_uid",
                "title": "Get Grafana Dashboard by UID",
                "description": "Retrieves a Grafana dashboard by its UID.",
                "inputSchema": GetDashboardByUidArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "list_grafana_teams",
                "title": "List Grafana Teams",
                "description": "Lists all teams in Grafana.",
                "inputSchema": ListTeamsArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "list_grafana_users",
                "title": "List Grafana Users",
                "description": "Lists all users in a Grafana organization.",
                "inputSchema": ListUsersArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "check_zabbix_query",
                "title": "Check Zabbix Query",
                "description": "Checks if a Zabbix query is valid.",
                "inputSchema": CheckZabbixQueryArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "get_zabbix_data",
                "title": "Get Zabbix Data",
                "description": "Gets a list of host groups and hosts from Zabbix.",
                "inputSchema": GetZabbixDataArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            }
        ]
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": {"tools": tools}})
    elif method == "tools/call":
        tool_name = body["params"]["name"]
        tool_args = body["params"].get("arguments", {})
        try:
            if tool_name == "create_grafana_dashboard":
                args = CreateDashboardArgs(**tool_args)
                result = create_grafana_dashboard(args)
                if isinstance(result, dict) and "error" in result:
                    return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": result["error"]}})
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
            elif tool_name == "delete_grafana_dashboard":
                args = DeleteDashboardArgs(**tool_args)
                result = delete_grafana_dashboard(args)
                if isinstance(result, dict) and "error" in result:
                    return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": result["error"]}})
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
            elif tool_name == "search_grafana_dashboards":
                args = SearchDashboardsArgs(**tool_args)
                result = search_grafana_dashboards(args)
                if isinstance(result, dict) and "error" in result:
                    return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": result["error"]}})
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
            elif tool_name == "get_grafana_dashboard_by_uid":
                args = GetDashboardByUidArgs(**tool_args)
                result = get_grafana_dashboard_by_uid(args)
                if isinstance(result, dict) and "error" in result:
                    return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": result["error"]}})
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
            elif tool_name == "list_grafana_teams":
                args = ListTeamsArgs(**tool_args)
                result = list_grafana_teams(args)
                if isinstance(result, dict) and "error" in result:
                    return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": result["error"]}})
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
            elif tool_name == "list_grafana_users":
                args = ListUsersArgs(**tool_args)
                result = list_grafana_users(args)
                if isinstance(result, dict) and "error" in result:
                    return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": result["error"]}})
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
            elif tool_name == "check_zabbix_query":
                args = CheckZabbixQueryArgs(**tool_args)
                result = check_zabbix_query(args)
                if isinstance(result, dict) and "error" in result:
                    return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": result["error"]}})
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
            elif tool_name == "get_zabbix_data":
                args = GetZabbixDataArgs(**tool_args)
                result = get_zabbix_data(args)
                if isinstance(result, dict) and "error" in result:
                    return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": result["error"]}})
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
            else:
                return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32601, "message": "Method not found"}}, status_code=404)
        except Exception as e:
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32000, "message": f"Internal server error: {e}"}}, status_code=500)
        else:
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32601, "message": "Method not found"}}, status_code=404)
    else:
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": None})

# --- FastAPI App ---
app = FastAPI()
app.include_router(router, prefix="/api/v1")