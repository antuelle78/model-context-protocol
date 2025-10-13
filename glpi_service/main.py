import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import get_db, engine
from .models import Base
from .schemas import GetGlpiFullAssetDumpArgs
from .glpi_api_service import glpi_service

# Create the database tables for this service
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GLPI Tools Service", version="1.0.0")

@app.get("/glpi/laptop_count")
async def get_glpi_laptop_count_endpoint(db: Session = Depends(get_db)):
    """
    Returns the number of laptops in GLPI.
    """
    count = glpi_service.get_asset_count(itemtype="Computer", query_params={"criteria[0][field]": "type", "criteria[0][searchtype]": "contains", "criteria[0][value]": "laptop"})
    return {"count": count, "message": f"There are {count} laptops in GLPI."}

@app.get("/glpi/pc_count")
async def get_glpi_pc_count_endpoint(db: Session = Depends(get_db)):
    """
    Returns the number of PCs (desktop computers) in GLPI.
    """
    count = glpi_service.get_asset_count(itemtype="Computer", query_params={"criteria[0][field]": "type", "criteria[0][searchtype]": "contains", "criteria[0][value]": "desktop"})
    return {"count": count, "message": f"There are {count} desktop PCs in GLPI."}

@app.get("/glpi/monitor_count")
async def get_glpi_monitor_count_endpoint(db: Session = Depends(get_db)):
    """
    Returns the number of monitors in GLPI.
    """
    count = glpi_service.get_asset_count(itemtype="Monitor")
    return {"count": count, "message": f"There are {count} monitors in GLPI."}

@app.get("/glpi/os_distribution")
async def get_glpi_os_distribution_endpoint(db: Session = Depends(get_db)):
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
        return {"report": "No operating system information found for computers in GLPI."}

    report_lines = ["Operating System Distribution in GLPI:"]
    for os_name, count in os_counts.items():
        report_lines.append(f"- {os_name}: {count}")
    return {"report": "\n".join(report_lines)}

@app.get("/glpi/full_asset_dump")
async def get_glpi_full_asset_dump_endpoint(args: GetGlpiFullAssetDumpArgs = Depends(), db: Session = Depends(get_db)):
    """
    Returns a complete dump of all assets of a specified type from GLPI.
    """
    assets = glpi_service.get_full_asset_dump(itemtype=args.itemtype)
    if not assets:
        return {"assets": [], "message": f"No assets found for type {args.itemtype} in GLPI."}
    return {"assets": assets}

@app.get("/glpi/inventory")
async def fetch_all_glpi_inventory_endpoint(db: Session = Depends(get_db)):
    """
    Fetches all inventory from GLPI.
    """
    inventory = glpi_service.fetch_and_store_inventory()
    return {"inventory": inventory}

