import httpx
from sqlalchemy.orm import Session
from .models import Ticket
from .schemas import TicketCreateRequest, TicketCreationResponse
from .config import settings

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
    return db.query(Ticket).filter(Ticket.state == "Resolved").order_by(Ticket.sys_updated_on.desc()).limit(10).all()
