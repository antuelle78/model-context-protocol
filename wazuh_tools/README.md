# Wazuh Tools API

This project provides a set of tools to interact with the Wazuh API.

## Deployment

To deploy the application to a k3s cluster, apply the `wazuh-tools-deployment.yaml` manifest:

```
kubectl apply -f wazuh-tools-deployment.yaml
```

## Client Connection

To connect to the Wazuh Tools API, you can use the following `curl` command:

```
curl -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "id": "1", "method": "tools/list", "params": {}}' http://<NODE_IP>:30085/api/v1/mcp
```

## Open-WebUI Configuration

To use the Wazuh Tools API with Open-WebUI, you need to place the `open-webui-client.py` file in the `tools` directory of your Open-WebUI installation.

Make sure to replace the `<NODE_IP>` placeholder in the `open-webui-client.py` file with the actual IP address of your k3s cluster node.

## LM Studio Configuration

To use the Wazuh Tools API with LM Studio, you need to copy the `mcp.json` file to the LM Studio configuration directory.

Make sure to replace the `<NODE_IP>` placeholder in the `mcp.json` file with the actual IP address of your k3s cluster node.

## Available Tools

- **get_agents**: Gets a list of all Wazuh agents.
- **get_agent_details**: Gets the details of a specific Wazuh agent.
- **get_rules**: Gets a list of all Wazuh rules.
- **get_alerts**: Gets a list of all Wazuh alerts.
- **add_agent**: Adds a new agent.
- **delete_agents**: Deletes one or more agents.
- **restart_agents**: Restarts one or more agents.
- **get_agent_key**: Returns the key of an agent.
- **get_vulnerabilities**: Gets the vulnerabilities of a specific agent.