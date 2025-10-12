import io
import csv
from sqlalchemy.orm import Session
from app import services
from app.schemas import (
    TicketCreateRequest,
    GenerateOpenTicketsByPriorityReportArgs,
    GenerateTicketsByAssignmentGroupReportArgs,
    CreateNewTicketArgs,
)

import anyio

# Function to generate a CSV report of open tickets by priority
async def generate_open_tickets_by_priority_report(db: Session, args: GenerateOpenTicketsByPriorityReportArgs):
    """
    Generates a CSV report of open tickets by priority.
    """
    # Get the tickets from the database
    tickets = await anyio.to_thread.run_sync(services.get_tickets_by_priority, db, args.priority)
    
    # Create a CSV report in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write the header row
    writer.writerow(["Number", "Short Description", "Assignment Group"])
    # Write the ticket data
    for ticket in tickets:
        writer.writerow([ticket.number, ticket.short_description, ticket.assignment_group])

    # Return the CSV report as a string
    return output.getvalue()

# Function to generate a CSV report of tickets by assignment group
async def generate_tickets_by_assignment_group_report(db: Session, args: GenerateTicketsByAssignmentGroupReportArgs):
    """
    Generates a CSV report of tickets by assignment group.
    """
    # Get the tickets from the database
    tickets = await anyio.to_thread.run_sync(services.get_tickets_by_assignment_group, db, args.group)
    
    # Create a CSV report in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write the header row
    writer.writerow(["Number", "Short Description", "Priority", "State"])
    # Write the ticket data
    for ticket in tickets:
        writer.writerow([ticket.number, ticket.short_description, ticket.priority, ticket.state])

    # Return the CSV report as a string
    return output.getvalue()

# Function to generate a CSV report of recently resolved tickets
async def generate_recently_resolved_tickets_report(db: Session):
    """
    Generates a CSV report of recently resolved tickets.
    """
    # Get the tickets from the database
    tickets = await anyio.to_thread.run_sync(services.get_recently_resolved_tickets, db)
    
    # Create a CSV report in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write the header row
    writer.writerow(["Number", "Short Description", "Resolved On"])
    # Write the ticket data
    for ticket in tickets:
        writer.writerow([ticket.number, ticket.short_description, ticket.sys_updated_on])

    # Return the CSV report as a string
    return output.getvalue()

# Function to create a new ticket in the ITSM system
async def create_new_ticket(db: Session, args: CreateNewTicketArgs):
    """
    Creates a new ticket in the ITSM system.
    """
    # Create a ticket create request object
    ticket_data = TicketCreateRequest(
        short_description=args.short_description,
        assignment_group=args.assignment_group,
        priority=args.priority,
    )
    # Create the ticket in the ITSM system
    created_ticket = await services.create_ticket(db, ticket_data)
    # Return a success message
    return f"Ticket {created_ticket.number} created successfully with priority {created_ticket.priority} and assigned to {created_ticket.assignment_group}."
