from glpi_api import GLPI
from .config import settings



class GlpiService:
    def __init__(self):
        self.glpi = GLPI(
            url=settings.GLPI_API_URL,
            apptoken=settings.GLPI_APP_TOKEN,
            auth=(settings.GLPI_USERNAME, settings.GLPI_PASSWORD)
        )

    def get_asset_count(self, itemtype: str, query_params: dict = None) -> int:
        # The glpi-api library doesn't have a direct count method.
        # We'll fetch all items and count them for simplicity for now.
        # In a real-world scenario, you'd want to use pagination and optimize.
        criteria_list = [query_params] if query_params else []
        items = self.glpi.search(itemtype, criteria=criteria_list)
        return len(items)

    def get_assets(self, itemtype: str, query_params: dict = None) -> list:
        criteria_list = [query_params] if query_params else []
        return self.glpi.search(itemtype, criteria=criteria_list)

    def get_full_asset_dump(self, itemtype: str) -> list:
        # Fetch all items of a given type, handling pagination if necessary
        # The glpi-api's search method should handle pagination automatically
        return self.glpi.search(itemtype, criteria=[{"expand_dropdowns": True}])

glpi_service = GlpiService()