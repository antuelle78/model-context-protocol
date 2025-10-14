import io
import csv
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Assuming these files will be copied into servicenow_service/
from .database import get_db, engine
from .models import Base, Ticket
from . import services
from .schemas import (
    TicketCreateRequest,
    GenerateOpenTicketsByPriorityReportArgs,
    GenerateTicketsByAssignmentGroupReportArgs,
    CreateNewTicketArgs,
    TicketCreationResponse, # Assuming this is needed for create_new_ticket return
)

# Create the database tables for this service
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ServiceNow Tools Service", version="1.0.0")

def to_csv_string(tickets: List[Ticket]):
    if not tickets:
        return ""
    output = io.StringIO()
    writer = csv.writer(output)
    # Write header from the first ticket's attributes
    writer.writerow([c.key for c in Ticket.__table__.columns])
    # Write rows
    for ticket in tickets:
        writer.writerow([getattr(ticket, c.key) for c in Ticket.__table__.columns])
    return output.getvalue()

# Function to generate a CSV report of open tickets by priority
@app.get("/servicenow/reports/open_by_priority")
async def generate_open_tickets_by_priority_report_endpoint(
    priority: str, db: Session = Depends(get_db)
):
    """
    Generates a CSV report of open tickets by priority.
    """
    tickets = services.get_tickets_by_priority(db, priority)
    report = to_csv_string(tickets)
    return {"data": report}

# Function to generate a CSV report of tickets by assignment group
@app.get("/servicenow/reports/by_assignment_group")
async def generate_tickets_by_assignment_group_report_endpoint(
    group: str, db: Session = Depends(get_db)
):
    """
    Generates a CSV report of tickets by assignment group.
    """
    tickets = services.get_tickets_by_assignment_group(db, group)
    report = to_csv_string(tickets)
    return {"data": report}

# Function to generate a CSV report of recently resolved tickets
@app.get("/servicenow/reports/recently_resolved")
async def generate_recently_resolved_tickets_report_endpoint(db: Session = Depends(get_db)):
    """
    Generates a CSV report of recently resolved tickets.
    """
    tickets = services.get_recently_resolved_tickets(db)
    report = to_csv_string(tickets)
    return {"data": report}

# Function to create a new ticket in the ITSM system
@app.post("/servicenow/tickets/create")
async def create_new_ticket_endpoint(args: CreateNewTicketArgs, db: Session = Depends(get_db)):
    """
    Creates a new ticket in the ITSM system.
    """
    ticket_data = TicketCreateRequest(
        short_description=args.short_description,
        assignment_group=args.assignment_group,
        priority=args.priority,
    )
    created_ticket = await services.create_ticket(db, ticket_data)
    return {"data": created_ticket.dict()}

@app.post("/servicenow/tickets/fetch_all_servicenow_tickets")
async def fetch_all_servicenow_tickets_endpoint(db: Session = Depends(get_db)):
    """
    Fetches the latest tickets from ServiceNow and stores them in the database.
    """
    print("Received request for /servicenow/tickets/fetch_all_servicenow_tickets")
    result = await services.fetch_and_store_tickets(db)
    print(f"Returning from /servicenow/tickets/fetch_all_servicenow_tickets: {result}")
    return {"data": result}
