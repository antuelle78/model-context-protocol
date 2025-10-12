import os
import requests
from pydantic import BaseModel, Field

class Tools:
    def __init__(self):
        self.backend_url = "http://localhost:8000"

import os
import requests
from pydantic import BaseModel, Field

class Tools:
    def __init__(self):
        self.backend_url = "http://localhost:8000" # Or the IP address of your MCP server

    def fetch_all_tickets(self) -> str:
        """
        Fetches the latest tickets from the ITSM and stores them in the database.
        """
        try:
            response = requests.post(f"{self.backend_url}/api/v1/tickets/fetch")
            response.raise_for_status()
            return response.json()["message"]
        except requests.RequestException as e:
            return f"Error fetching tickets: {str(e)}"

    def get_report_open_by_priority(self, priority: str = Field(..., description="The priority of the tickets to include in the report.")) -> str:
        """
        Generates a CSV report of open tickets by priority.
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/reports/open_by_priority?priority={priority}")
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Error generating report: {str(e)}"

    def get_report_by_assignment_group(self, group: str = Field(..., description="The assignment group of the tickets to include in the report.")) -> str:
        """
        Generates a CSV report of tickets by assignment group.
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/reports/by_assignment_group?group={group}")
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Error generating report: {str(e)}"

    def get_report_recently_resolved(self) -> str:
        """
        Generates a CSV report of recently resolved tickets.
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/reports/recently_resolved")
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Error generating report: {str(e)}"

    def get_glpi_laptop_count(self) -> str:
        """
        Returns the number of laptops in GLPI.
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/glpi/laptop_count")
            response.raise_for_status()
            return response.json()["count"]
        except requests.RequestException as e:
            return f"Error fetching laptop count: {str(e)}"

    def get_glpi_pc_count(self) -> str:
        """
        Returns the number of PCs (desktop computers) in GLPI.
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/glpi/pc_count")
            response.raise_for_status()
            return response.json()["count"]
        except requests.RequestException as e:
            return f"Error fetching PC count: {str(e)}"

    def get_glpi_monitor_count(self) -> str:
        """
        Returns the number of monitors in GLPI.
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/glpi/monitor_count")
            response.raise_for_status()
            return response.json()["count"]
        except requests.RequestException as e:
            return f"Error fetching monitor count: {str(e)}"

    def get_glpi_os_distribution(self) -> str:
        """
        Returns a breakdown of operating system usage across computers in GLPI.
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/glpi/os_distribution")
            response.raise_for_status()
            return response.json()["report"]
        except requests.RequestException as e:
            return f"Error fetching OS distribution: {str(e)}"

    def get_glpi_full_asset_dump(self, itemtype: str = Field(..., description="The type of asset to dump (e.g., Computer, Monitor).")) -> str:
        """
        Returns a complete dump of all assets of a specified type from GLPI.
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/glpi/full_asset_dump?itemtype={itemtype}")
            response.raise_for_status()
            return response.json()["assets"]
        except requests.RequestException as e:
            return f"Error fetching full asset dump: {str(e)}"
