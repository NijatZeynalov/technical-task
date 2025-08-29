import os
from typing import List
from fastapi import FastAPI, HTTPException
from app.agent import TicketAgent
from app import crud, models, schemas

if os.getenv("DYNAMODB_HOST"):
    os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"

# --- Agent Initialization ---

agent = TicketAgent()

app = FastAPI(
    title="Helpdesk Ticketing API",
    description="A serverless API for a helpdesk ticketing system using FastAPI and DynamoDB.",
    version="1.0.0"
)

# --- API Endpoints ---

@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/tickets", response_model=schemas.TicketResponse, status_code=201, tags=["Tickets"])
def create_ticket(ticket_in: schemas.TicketCreate):
    """
    Create a new helpdesk ticket.
    - A new ticket is created in the `Ticket` table.
    - The ticket is processed by an AI agent to add relevant tags.
    - A corresponding version 1 record is created in the `TicketHistory` table.
    """
    suggested_tags = agent.process_ticket(ticket_in.title, ticket_in.description)
    ticket = crud.create_ticket(ticket_in, suggested_tags)
    return ticket


@app.get("/tickets", response_model=List[schemas.TicketResponse], tags=["Tickets"])
def list_tickets():
    """
    Retrieve all current tickets.
    """
    return crud.get_tickets()


@app.get("/tickets/{ticket_id}", response_model=schemas.TicketResponse, tags=["Tickets"])
def get_ticket(ticket_id: str):
    """
    Retrieve the current state of a specific ticket.
    """
    ticket = crud.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.put("/tickets/{ticket_id}", response_model=schemas.TicketResponse, tags=["Tickets"])
def update_ticket(ticket_id: str, ticket_in: schemas.TicketUpdate):
    """
    Update an existing ticket.
    - The ticket's version is incremented.
    - The `Ticket` table is updated with the new state.
    - A new record is created in the `TicketHistory` table with the updated state.
    """
    ticket = crud.update_ticket(ticket_id, ticket_in)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.get("/tickets/{ticket_id}/history", response_model=List[schemas.TicketHistoryResponse], tags=["Tickets"])
def get_ticket_history(ticket_id: str):
    """
    Retrieve the full version history of a specific ticket.
    """
    history = crud.get_ticket_history(ticket_id)
    if not history:
        raise HTTPException(status_code=404, detail="Ticket not found or has no history")
    return history
