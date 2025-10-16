
import json

def create_panel(title, datasource, group, host, application, item, x, y):
    return {
        "title": title,
        "type": "graph",
        "datasource": datasource,
        "gridPos": {"h": 8, "w": 4, "x": x, "y": y},
        "targets": [
            {
                "group": {"filter": group},
                "host": {"filter": host},
                "application": {"filter": application},
                "item": {"filter": item}
            }
        ]
    }

dashboard = {
    "dashboard": {
        "title": "Zabbix Host Groups Overview",
        "panels": [
            # Linux Servers
            create_panel("Linux CPU Usage", "alexanderzobnin-zabbix-datasource", "Linux Servers", "*", "CPU", "CPU utilization", 0, 0),
            create_panel("Linux Memory Usage", "alexanderzobnin-zabbix-datasource", "Linux Servers", "*", "Memory", "Memory utilization", 4, 0),
            create_panel("Linux Disk Space", "alexanderzobnin-zabbix-datasource", "Linux Servers", "*", "Filesystem", "Free disk space on /", 8, 0),
            # Windows Servers
            create_panel("Windows CPU Usage", "alexanderzobnin-zabbix-datasource", "Windows Servers", "*", "CPU", "CPU utilization", 0, 8),
            create_panel("Windows Memory Usage", "alexanderzobnin-zabbix-datasource", "Windows Servers", "*", "Memory", "Memory utilization", 4, 8),
            create_panel("Windows Disk Space", "alexanderzobnin-zabbix-datasource", "Windows Servers", "*", "Filesystem", "Free disk space on C:", 8, 8),
            # Network Appliances
            create_panel("Network CPU Usage", "alexanderzobnin-zabbix-datasource", "Network Appliances", "*", "CPU", "CPU utilization", 0, 16),
            create_panel("Network Memory Usage", "alexanderzobnin-zabbix-datasource", "Network Appliances", "*", "Memory", "Memory utilization", 4, 16),
            # Storage Devices
            create_panel("Storage CPU Usage", "alexanderzobnin-zabbix-datasource", "Storage Devices", "*", "CPU", "CPU utilization", 0, 24),
            create_panel("Storage Memory Usage", "alexanderzobnin-zabbix-datasource", "Storage Devices", "*", "Memory", "Memory utilization", 4, 24),
        ]
    }
}

with open("dashboard.json", "w") as f:
    f.write(json.dumps(dashboard))
