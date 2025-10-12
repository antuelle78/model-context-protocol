import httpx
from sqlalchemy.orm import Session
from app.models import Ticket
from app.schemas import TicketCreateRequest, TicketCreationResponse
from app.config import settings

async def fetch_and_store_tickets(
    service_name: str,
    glpi_base_url: str = None,
    glpi_app_token: str = None,
    glpi_access_token: str = None,
    servicenow_base_url: str = None,
    servicenow_username: str = None,
    servicenow_password: str = None
) -> List[Dict[str, Any]]:
    """
    Fetches tickets from the specified service (GLPI or ServiceNow) and stores them in the database.
    """
    db = next(get_db())
    tickets_data = []

    # Use settings from config.py if not provided as arguments
    glpi_base_url = glpi_base_url or settings.GLPI_API_URL
    glpi_app_token = glpi_app_token or settings.GLPI_APP_TOKEN
    glpi_access_token = glpi_access_token or settings.GLPI_ACCESS_TOKEN
    servicenow_base_url = servicenow_base_url or settings.SERVICE_MANAGER_API_URL
    servicenow_username = servicenow_username or settings.SERVICENOW_USERNAME
    servicenow_password = servicenow_password or settings.SERVICENOW_PASSWORD

    if service_name.lower() == "glpi":
        if not glpi_base_url or not glpi_app_token or not glpi_access_token:
            raise ValueError("GLPI configuration (base_url, app_token, access_token) must be provided.")
        glpi_tools = GLPITools(glpi_base_url, glpi_app_token, glpi_access_token)
        tickets_data = await glpi_tools.get_all_tickets()
    elif service_name.lower() == "servicenow":
        if not servicenow_base_url or not servicenow_username or not servicenow_password:
            raise ValueError("ServiceNow configuration (base_url, username, password) must be provided.")
        servicenow_tools = ServiceNowTools(servicenow_base_url, servicenow_username, servicenow_password)
        tickets_data = await servicenow_tools.get_all_tickets()
    else:
        raise ValueError(f"Unsupported service: {service_name}")

    stored_tickets = []
    for ticket_data in tickets:
        ticket = TicketCreate(**ticket_data)
        db_ticket = Ticket(**ticket.dict())
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        stored_tickets.append(db_ticket)
    return stored_tickets

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
