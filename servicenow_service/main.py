import io
import csv
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Assuming these files will be copied into servicenow_service/
from .database import get_db, engine
from .models import Base
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

# Function to generate a CSV report of open tickets by priority
@app.get("/servicenow/reports/open_by_priority")
async def generate_open_tickets_by_priority_report_endpoint(
    priority: str, db: Session = Depends(get_db)
):
    """
    Generates a CSV report of open tickets by priority.
    """
    report = await services.generate_open_tickets_by_priority_report(db, priority)
    return {"report": report}

# Function to generate a CSV report of tickets by assignment group
@app.get("/servicenow/reports/by_assignment_group")
async def generate_tickets_by_assignment_group_report_endpoint(
    group: str, db: Session = Depends(get_db)
):
    """
    Generates a CSV report of tickets by assignment group.
    """
    report = await services.generate_tickets_by_assignment_group_report(db, group)
    return {"report": report}

# Function to generate a CSV report of recently resolved tickets
@app.get("/servicenow/reports/recently_resolved")
async def generate_recently_resolved_tickets_report_endpoint(db: Session = Depends(get_db)):
    """
    Generates a CSV report of recently resolved tickets.
    """
    report = await services.generate_recently_resolved_tickets_report(db)
    return {"report": report}

# Function to create a new ticket in the ITSM system
@app.post("/servicenow/tickets/create")
async def create_new_ticket_endpoint(args: CreateNewTicketArgs, db: Session = Depends(get_db)):
    """
    Creates a new ticket in the ITSM system.
    """
    created_ticket_message = await services.create_new_ticket(db, args)
    return {"message": created_ticket_message}

@app.post("/servicenow/tickets/fetch_all_servicenow_tickets")
async def fetch_all_servicenow_tickets_endpoint(db: Session = Depends(get_db)):
    """
    Fetches the latest tickets from ServiceNow and stores them in the database.
    """
    print("Received request for /servicenow/tickets/fetch_all_servicenow_tickets")
    result = await services.fetch_and_store_tickets(db)
    print(f"Returning from /servicenow/tickets/fetch_all_servicenow_tickets: {result}")
    return result
