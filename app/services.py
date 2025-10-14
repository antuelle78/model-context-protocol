from typing import Any, Dict
import httpx
from sqlalchemy.orm import Session
from app.models import Ticket
from app.schemas import TicketCreateRequest, TicketCreationResponse
from app.config import settings

async def fetch_and_store_tickets(db: Session):
    auth = (settings.SERVICENOW_USERNAME, settings.SERVICENOW_PASSWORD)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.SERVICE_MANAGER_API_URL}/now/table/incident?sysparm_display_value=true",
            auth=auth
        )
        response.raise_for_status()
        tickets = response.json()["result"]

        for ticket_data in tickets:
            ticket = db.query(Ticket).filter(Ticket.number == ticket_data["number"]).first()
            if ticket:
                # Update existing ticket
                for key, value in ticket_data.items():
                    if hasattr(ticket, key):
                        setattr(ticket, key, value)
            else:
                # Create new ticket
                ticket = Ticket(**{k: v for k, v in ticket_data.items() if k in Ticket.__table__.columns.keys()})
                db.add(ticket)
        db.commit()
        return {"message": "Tickets fetched and stored successfully."}

async def create_ticket(db: Session, ticket_data: TicketCreateRequest) -> TicketCreationResponse:
    auth = (settings.SERVICENOW_USERNAME, settings.SERVICENOW_PASSWORD)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.SERVICE_MANAGER_API_URL}/now/table/incident",
            auth=auth,
            json={
                "short_description": ticket_data.short_description,
                "assignment_group": ticket_data.assignment_group,
                "priority": ticket_data.priority,
            }
        )
        response.raise_for_status()
        created_ticket_data = response.json()["result"]

        # Store the created ticket in the local database
        ticket = Ticket(**{k: v for k, v in created_ticket_data.items() if k in Ticket.__table__.columns.keys()})
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return TicketCreationResponse(**created_ticket_data)

def get_tickets_by_priority(db: Session, priority: str):
    return db.query(Ticket).filter(Ticket.priority == priority).all()

def get_tickets_by_assignment_group(db: Session, group: str):
    return db.query(Ticket).filter(Ticket.assignment_group == group).all()

def get_recently_resolved_tickets(db: Session):
    try:
        tickets = db.query(Ticket).filter(Ticket.state == "Resolved").order_by(Ticket.sys_updated_on.desc()).limit(10).all()
        return [ticket.__dict__ for ticket in tickets]
    except Exception as e:
        import traceback
        print(f"Error in get_recently_resolved_tickets: {e}")
        traceback.print_exc()
        raise

from glpi_api import GLPI

class GlpiService:
    def __init__(self):
        try:
            self.glpi = GLPI(
                url=settings.GLPI_API_URL,
                apptoken=settings.GLPI_APP_TOKEN,
                auth=(settings.GLPI_USERNAME, settings.GLPI_PASSWORD)
            )
        except Exception as e:
            self.glpi = None
            print(f"Failed to initialize GLPI API: {e}")

    def _check_init(self):
        if not self.glpi:
            raise Exception("GLPI connection not configured or failed to initialize.")

    def get_asset_count(self, itemtype: str, query_params: dict = None) -> int:
        self._check_init()
        # The glpi-api library doesn't have a direct count method.
        # We'll fetch all items and count them for simplicity for now.
        # In a real-world scenario, you'd want to use pagination and optimize.
        criteria_list = [query_params] if query_params else []
        items = self.glpi.search(itemtype, criteria=criteria_list)
        return len(items)

    def get_assets(self, itemtype: str, query_params: dict = None) -> list:
        self._check_init()
        criteria_list = [query_params] if query_params else []
        return self.glpi.search(itemtype, criteria=criteria_list)

    def get_full_asset_dump(self, itemtype: str) -> list:
        self._check_init()
        # Fetch all items of a given type, handling pagination if necessary
        # The glpi-api's search method should handle pagination automatically
        return self.glpi.search(itemtype, criteria=[{"expand_dropdowns": True}])

    def fetch_and_store_inventory(self) -> list:
        self._check_init()
        # For now, just fetch all computers and return them.
        # In a real-world scenario, you would store this in a database.
        return self.glpi.search("Computer")

glpi_service = GlpiService()

import os

def read_directory(path: str):
    """
    Reads all files from a given directory and returns their content.
    """
    if not os.path.isdir(path):
        raise ValueError("Invalid directory path")

    file_contents = {}
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                file_contents[filename] = f.read()

    return file_contents
