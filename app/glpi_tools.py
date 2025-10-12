import json
from sqlalchemy.orm import Session
from app.schemas import (
    GetGlpiFullAssetDumpArgs,
)
from app.glpi_service import glpi_service

async def get_glpi_laptop_count(db: Session):
    """
    Returns the number of laptops in GLPI.
    """
    # Assuming 'Computer' is the itemtype for laptops and PCs, and we can filter by type.
    # This might require more specific filtering based on GLPI's asset types/models.
    count = glpi_service.get_asset_count(itemtype="Computer", query_params={"criteria[0][field]": "type", "criteria[0][searchtype]": "contains", "criteria[0][value]": "laptop"})
    return f"There are {count} laptops in GLPI."

async def get_glpi_pc_count(db: Session):
    """
    Returns the number of PCs (desktop computers) in GLPI.
    """
    count = glpi_service.get_asset_count(itemtype="Computer", query_params={"criteria[0][field]": "type", "criteria[0][searchtype]": "contains", "criteria[0][value]": "desktop"})
    return f"There are {count} desktop PCs in GLPI."

async def get_glpi_monitor_count(db: Session):
    """
    Returns the number of monitors in GLPI.
    """
    count = glpi_service.get_asset_count(itemtype="Monitor")
    return f"There are {count} monitors in GLPI."

async def get_glpi_os_distribution(db: Session):
    """
    Returns a breakdown of operating system usage across computers in GLPI.
    """
    computers = glpi_service.get_assets(itemtype="Computer", query_params={"expand_dropdowns": True, "with_operatingsystems": True})
    os_counts = {}
    for computer in computers:
        if "operatingsystems" in computer and computer["operatingsystems"]:
            for os_info in computer["operatingsystems"]:
                os_name = os_info.get("name", "Unknown OS")
                os_counts[os_name] = os_counts.get(os_name, 0) + 1
    
    if not os_counts:
        return "No operating system information found for computers in GLPI."

    report = "Operating System Distribution in GLPI:\n"
    for os_name, count in os_counts.items():
        report += f"- {os_name}: {count}\n"
    return report

async def get_glpi_full_asset_dump(db: Session, args: GetGlpiFullAssetDumpArgs):
    """
    Returns a complete dump of all assets of a specified type from GLPI.
    """
    assets = glpi_service.get_full_asset_dump(itemtype=args.itemtype)
    if not assets:
        return f"No assets found for type {args.itemtype} in GLPI."
    return json.dumps(assets, indent=2)

