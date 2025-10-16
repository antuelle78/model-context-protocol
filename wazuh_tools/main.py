from fastapi import FastAPI, APIRouter, Request
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import os
import json

import logging

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Pydantic Schemas ---
class GetAgentDetailsArgs(BaseModel):
    agent_id: str = Field(..., description="The ID of the agent to get details for.")

class GetAgentsArgs(BaseModel):
    offset: int = Field(0, description="The offset for pagination.")
    limit: int = Field(500, description="The limit for pagination.")
    status: str = Field(None, description="Filter by agent status (use commas to enter multiple statuses).")
    q: str = Field(None, description='Query to filter results by. For example q="status=active"')
    os_platform: str = Field(None, description="Filter by OS platform", alias="os.platform")
    os_version: str = Field(None, description="Filter by OS version", alias="os.version")
    os_name: str = Field(None, description="Filter by OS name", alias="os.name")
    manager: str = Field(None, description="Filter by manager hostname where agents are connected to")
    version: str = Field(None, description="Filter by agents version")
    group: str = Field(None, description="Filter by group of agents")
    node_name: str = Field(None, description="Filter by node name")
    name: str = Field(None, description="Filter by name")
    ip: str = Field(None, description="Filter by the IP used by the agent to communicate with the manager.")
    registerIP: str = Field(None, description="Filter by the IP used when registering the agent")
    group_config_status: str = Field(None, description="Agent groups configuration sync status")
    sort: str = Field(None, description="Sort the collection by a field or fields (separated by comma).")
    search: str = Field(None, description="Look for elements containing the specified string.")
    select: str = Field(None, description="Select which fields to return (separated by comma).")
    distinct: bool = Field(False, description="Look for distinct values.")

class GetRulesArgs(BaseModel):
    offset: int = Field(0, description="The offset for pagination.")
    limit: int = Field(500, description="The limit for pagination.")
    status: str = Field(None, description="Filter by rule status.")
    q: str = Field(None, description="Query to filter results by.")
    group: str = Field(None, description="Filter by group of rules.")
    pci_dss: str = Field(None, description="Filter by pci_dss requirement.")
    gdpr: str = Field(None, description="Filter by gdpr requirement.")
    hipaa: str = Field(None, description="Filter by hipaa requirement.")
    nist_800_53: str = Field(None, description="Filter by nist_800_53 requirement.")
    tsc: str = Field(None, description="Filter by tsc requirement.")
    mitre: str = Field(None, description="Filter by mitre requirement.")
    sort: str = Field(None, description="Sort the collection by a field or fields (separated by comma).")
    search: str = Field(None, description="Look for elements containing the specified string.")
    select: str = Field(None, description="Select which fields to return (separated by comma).")

class GetAlertsArgs(BaseModel):
    offset: int = Field(0, description="The offset for pagination.")
    limit: int = Field(500, description="The limit for pagination.")
    agents_list: str = Field(None, description="List of agent IDs (separated by comma).")
    rule_ids: str = Field(None, description="List of rule IDs (separated by comma).", alias="rule.ids")
    rule_description: str = Field(None, description="Filter by rule description.", alias="rule.description")
    rule_level: str = Field(None, description="Filter by rule level.", alias="rule.level")
    rule_groups: str = Field(None, description="Filter by rule groups.", alias="rule.groups")
    rule_pci_dss: str = Field(None, description="Filter by rule pci_dss requirement.", alias="rule.pci_dss")
    rule_gdpr: str = Field(None, description="Filter by rule gdpr requirement.", alias="rule.gdpr")
    rule_hipaa: str = Field(None, description="Filter by rule hipaa requirement.", alias="rule.hipaa")
    rule_nist_800_53: str = Field(None, description="Filter by rule nist_800_53 requirement.", alias="rule.nist_800_53")
    rule_tsc: str = Field(None, description="Filter by rule tsc requirement.", alias="rule.tsc")
    rule_mitre: str = Field(None, description="Filter by rule mitre requirement.", alias="rule.mitre")
    location: str = Field(None, description="Filter by location.")
    user: str = Field(None, description="Filter by user.")
    sort: str = Field(None, description="Sort the collection by a field or fields (separated by comma).")
    search: str = Field(None, description="Look for elements containing the specified string.")
    select: str = Field(None, description="Select which fields to return (separated by comma).")

# --- Tool Implementation ---
def get_auth_token():
    """
    Gets the authentication token from the Wazuh API.
    """
    wazuh_user = os.environ.get("WAZUH_USER")
    wazuh_password = os.environ.get("WAZUH_PASSWORD")

    if not wazuh_user or not wazuh_password:
        logging.error("WAZUH_USER or WAZUH_PASSWORD environment variables not set.")
        return None

    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.post(f"{os.environ.get('WAZUH_URL')}/security/user/authenticate", auth=(wazuh_user, wazuh_password), verify=wazuh_ssl_verify)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error getting token: {json_response.get('message', 'Unknown error')}")
            return None
        return json_response.get("data", {}).get("token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting token: {e}")
        return None

def get_agents(args: GetAgentsArgs):
    """
    Gets a list of all Wazuh agents.
    """
    token = get_auth_token()
    if not token:
        return "Could not authenticate with the Wazuh API."

    headers = {"Authorization": f"Bearer {token}"}
    params = args.dict(by_alias=True, exclude_none=True)
    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.get(f"{os.environ.get('WAZUH_URL')}/agents", headers=headers, params=params, verify=wazuh_ssl_verify)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error getting agents: {json_response.get('message', 'Unknown error')}")
            return f"An error occurred: {json_response.get('message', 'Unknown error')}"
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting agents: {e}")
        return f"An error occurred: {e}"

def get_agent_details(args: GetAgentDetailsArgs):
    """
    Gets the details of a specific Wazuh agent.
    """
    return get_agents(GetAgentsArgs(agents_list=args.agent_id))

def get_rules(args: GetRulesArgs):
    """
    Gets a list of all Wazuh rules.
    """
    token = get_auth_token()
    if not token:
        return "Could not authenticate with the Wazuh API."

    headers = {"Authorization": f"Bearer {token}"}
    params = args.dict(by_alias=True, exclude_none=True)
    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.get(f"{os.environ.get('WAZUH_URL')}/rules", headers=headers, params=params, verify=wazuh_ssl_verify)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error getting rules: {json_response.get('message', 'Unknown error')}")
            return f"An error occurred: {json_response.get('message', 'Unknown error')}"
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting rules: {e}")
        return f"An error occurred: {e}"

def get_alerts(args: GetAlertsArgs):
    """
    Gets a list of all Wazuh alerts.
    """
    token = get_auth_token()
    if not token:
        return "Could not authenticate with the Wazuh API."

    headers = {"Authorization": f"Bearer {token}"}
    params = args.dict(by_alias=True, exclude_none=True)
    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.get(f"{os.environ.get('WAZUH_URL')}/alerts", headers=headers, params=params, verify=wazuh_ssl_verify)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error getting alerts: {json_response.get('message', 'Unknown error')}")
            return f"An error occurred: {json_response.get('message', 'Unknown error')}"
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting alerts: {e}")
        return f"An error occurred: {e}"

class AddAgentArgs(BaseModel):
    name: str = Field(..., description="Agent name")
    ip: str = Field(None, description="If this is not included, the API will get the IP automatically. Allowed values: IP, IP/NET, ANY")

def add_agent(args: AddAgentArgs):
    """
    Adds a new agent.
    """
    token = get_auth_token()
    if not token:
        return "Could not authenticate with the Wazuh API."

    headers = {"Authorization": f"Bearer {token}"}
    data = args.dict(exclude_none=True)
    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.post(f"{os.environ.get('WAZUH_URL')}/agents", headers=headers, json=data, verify=wazuh_ssl_verify)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error adding agent: {json_response.get('message', 'Unknown error')}")
            return f"An error occurred: {json_response.get('message', 'Unknown error')}"
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error adding agent: {e}")
        return f"An error occurred: {e}"

class DeleteAgentsArgs(BaseModel):
    agents_list: str = Field(..., description="List of agent IDs (separated by comma), use the keyword all to select all agents")
    purge: bool = Field(False, description="Permanently delete an agent from the key store.")
    status: str = Field(None, description="Filter by agent status (use commas to enter multiple statuses).")
    older_than: str = Field(None, description="Consider only agents whose last keep alive is older than the specified time frame.")
    q: str = Field(None, description="Query to filter results by.")
    os_platform: str = Field(None, description="Filter by OS platform", alias="os.platform")
    os_version: str = Field(None, description="Filter by OS version", alias="os.version")
    os_name: str = Field(None, description="Filter by OS name", alias="os.name")
    manager: str = Field(None, description="Filter by manager hostname where agents are connected to")
    version: str = Field(None, description="Filter by agents version")
    group: str = Field(None, description="Filter by group of agents")
    node_name: str = Field(None, description="Filter by node name")
    name: str = Field(None, description="Filter by name")
    ip: str = Field(None, description="Filter by the IP used by the agent to communicate with the manager.")
    registerIP: str = Field(None, description="Filter by the IP used when registering the agent")

def delete_agents(args: DeleteAgentsArgs):
    """
    Deletes one or more agents.
    """
    token = get_auth_token()
    if not token:
        return "Could not authenticate with the Wazuh API."

    headers = {"Authorization": f"Bearer {token}"}
    params = args.dict(by_alias=True, exclude_none=True)
    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.delete(f"{os.environ.get('WAZUH_URL')}/agents", headers=headers, params=params, verify=wazuh_ssl_verify)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error deleting agents: {json_response.get('message', 'Unknown error')}")
            return f"An error occurred: {json_response.get('message', 'Unknown error')}"
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error deleting agents: {e}")
        return f"An error occurred: {e}"

class RestartAgentsArgs(BaseModel):
    agents_list: str = Field(None, description="List of agent IDs (separated by comma), all agents selected by default if not specified")

def restart_agents(args: RestartAgentsArgs):
    """
    Restarts one or more agents.
    """
    token = get_auth_token()
    if not token:
        return "Could not authenticate with the Wazuh API."

    headers = {"Authorization": f"Bearer {token}"}
    params = args.dict(exclude_none=True)
    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.put(f"{os.environ.get('WAZUH_URL')}/agents/restart", headers=headers, params=params, verify=wazuh_ssl_verify)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error restarting agents: {json_response.get('message', 'Unknown error')}")
            return f"An error occurred: {json_response.get('message', 'Unknown error')}"
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error restarting agents: {e}")
        return f"An error occurred: {e}"

class GetAgentKeyArgs(BaseModel):
    agent_id: str = Field(..., description="Agent ID. All possible values from 000 onwards")

def get_agent_key(args: GetAgentKeyArgs):
    """
    Returns the key of an agent.
    """
    token = get_auth_token()
    if not token:
        return "Could not authenticate with the Wazuh API."

    headers = {"Authorization": f"Bearer {token}"}
    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.get(f"{os.environ.get('WAZUH_URL')}/agents/{args.agent_id}/key", headers=headers, verify=wazuh_ssl_verify)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error getting agent key: {json_response.get('message', 'Unknown error')}")
            return f"An error occurred: {json_response.get('message', 'Unknown error')}"
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting agent key: {e}")
        return f"An error occurred: {e}"

class GetVulnerabilitiesArgs(BaseModel):
    agent_id: str = Field(..., description="Agent ID.")
    offset: int = Field(0, description="First element to return in the collection.")
    limit: int = Field(500, description="Maximum number of elements to return.")
    sort: str = Field(None, description="Sort the collection by a field or fields.")
    search: str = Field(None, description="Look for elements containing the specified string.")
    select: str = Field(None, description="Select which fields to return.")
    q: str = Field(None, description="Query to filter results by.")
    distinct: bool = Field(False, description="Look for distinct values.")
    status: str = Field(None, description="Filter by vulnerability status.")
    type: str = Field(None, description="Filter by vulnerability type.")
    severity: str = Field(None, description="Filter by vulnerability severity.")
    architecture: str = Field(None, description="Filter by vulnerability architecture.")
    cve: str = Field(None, description="Filter by CVE ID.")
    name: str = Field(None, description="Filter by vulnerability name.")
    version: str = Field(None, description="Filter by vulnerability version.")

def get_vulnerabilities(args: GetVulnerabilitiesArgs):
    """
    Gets the vulnerabilities of a specific agent.
    """
    token = get_auth_token()
    if not token:
        return "Could not authenticate with the Wazuh API."

    headers = {"Authorization": f"Bearer {token}"}
    params = args.dict(by_alias=True, exclude_none=True)
    agent_id = params.pop("agent_id")
    wazuh_ssl_verify = os.environ.get("WAZUH_SSL_VERIFY", "true").lower() == "true"
    try:
        response = requests.get(f"{os.environ.get('WAZUH_URL')}/vulnerability/{agent_id}", headers=headers, params=params, verify=wazuh_ssl_verify)
        print(response.text)
        response.raise_for_status()
        json_response = response.json()
        if json_response.get("error", 0) != 0:
            logging.error(f"Error getting vulnerabilities: {json_response.get('message', 'Unknown error')}")
            return f"An error occurred: {json_response.get('message', 'Unknown error')}"
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting vulnerabilities: {e}")
        return f"An error occurred: {e}"

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
            "result": {"protocolVersion": "1.0.0", "serverInfo": {"name": "Wazuh Tool"}}
        })
    elif method == "tools/list":
        tools = [
            {
                "name": "get_agents",
                "title": "Get Wazuh Agents",
                "description": "Gets a list of all Wazuh agents.",
                "inputSchema": GetAgentsArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "get_agent_details",
                "title": "Get Wazuh Agent Details",
                "description": "Gets the details of a specific Wazuh agent.",
                "inputSchema": GetAgentDetailsArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "get_rules",
                "title": "Get Wazuh Rules",
                "description": "Gets a list of all Wazuh rules.",
                "inputSchema": GetRulesArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "get_alerts",
                "title": "Get Wazuh Alerts",
                "description": "Gets a list of all Wazuh alerts.",
                "inputSchema": GetAlertsArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "add_agent",
                "title": "Add Wazuh Agent",
                "description": "Adds a new agent.",
                "inputSchema": AddAgentArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "delete_agents",
                "title": "Delete Wazuh Agents",
                "description": "Deletes one or more agents.",
                "inputSchema": DeleteAgentsArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "restart_agents",
                "title": "Restart Wazuh Agents",
                "description": "Restarts one or more agents.",
                "inputSchema": RestartAgentsArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "get_agent_key",
                "title": "Get Wazuh Agent Key",
                "description": "Returns the key of an agent.",
                "inputSchema": GetAgentKeyArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            },
            {
                "name": "get_vulnerabilities",
                "title": "Get Agent Vulnerabilities",
                "description": "Gets the vulnerabilities of a specific agent.",
                "inputSchema": GetVulnerabilitiesArgs.model_json_schema(),
                "outputSchema": {"type": "object"}
            }
        ]
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": {"tools": tools}})
    elif method == "tools/call":
        tool_name = body["params"]["name"]
        tool_args = body["params"].get("arguments", {})
        logging.info(f"Calling tool: {tool_name} with args: {tool_args}")

        if tool_name == "get_agents":
            args = GetAgentsArgs(**tool_args)
            result = get_agents(args)
            logging.info(f"Tool get_agents returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "get_agent_details":
            args = GetAgentDetailsArgs(**tool_args)
            result = get_agent_details(args)
            logging.info(f"Tool get_agent_details returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "get_rules":
            args = GetRulesArgs(**tool_args)
            result = get_rules(args)
            logging.info(f"Tool get_rules returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "get_alerts":
            args = GetAlertsArgs(**tool_args)
            result = get_alerts(args)
            logging.info(f"Tool get_alerts returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "add_agent":
            args = AddAgentArgs(**tool_args)
            result = add_agent(args)
            logging.info(f"Tool add_agent returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "delete_agents":
            args = DeleteAgentsArgs(**tool_args)
            result = delete_agents(args)
            logging.info(f"Tool delete_agents returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "restart_agents":
            args = RestartAgentsArgs(**tool_args)
            result = restart_agents(args)
            logging.info(f"Tool restart_agents returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "get_agent_key":
            args = GetAgentKeyArgs(**tool_args)
            result = get_agent_key(args)
            logging.info(f"Tool get_agent_key returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        elif tool_name == "get_vulnerabilities":
            args = GetVulnerabilitiesArgs(**tool_args)
            result = get_vulnerabilities(args)
            logging.info(f"Tool get_vulnerabilities returned: {result}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": result})
        else:
            logging.error(f"Method not found: {tool_name}")
            return JSONResponse(content={"jsonrpc": "2.0", "id": id, "error": {"code": -32601, "message": "Method not found"}}, status_code=404)
    else:
        return JSONResponse(content={"jsonrpc": "2.0", "id": id, "result": None})

# --- FastAPI App ---
app = FastAPI()
app.include_router(router, prefix="/api/v1")