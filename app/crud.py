import uuid
from typing import List
from app.models import Ticket, TicketHistory
from app.schemas import TicketCreate, TicketUpdate


def _log_history(ticket: Ticket):
    TicketHistory(
        ticket_id=ticket.ticket_id,
        version=ticket.version,
        title=ticket.title,
        description=ticket.description,
        creator=ticket.creator,
        status=ticket.status,
        tags=ticket.tags,
    ).save()


def create_ticket(ticket_in: TicketCreate, suggested_tags: List[str]) -> Ticket:
    ticket = Ticket(
        ticket_id=str(uuid.uuid4()),
        **ticket_in.model_dump()
    )
    if suggested_tags:
        ticket.tags = suggested_tags
    ticket.save()
    _log_history(ticket)
    return ticket


def get_tickets() -> List[Ticket]:
    return list(Ticket.scan())


def get_ticket(ticket_id: str) -> Ticket:
    try:
        return Ticket.get(ticket_id)
    except Ticket.DoesNotExist:
        return None


def update_ticket(ticket_id: str, ticket_in: TicketUpdate) -> Ticket:
    try:
        ticket = Ticket.get(ticket_id)
        update_data = ticket_in.model_dump(exclude_unset=True)
        if not update_data:
            return None

        actions = []
        for key, value in update_data.items():
            if hasattr(Ticket, key):
                actions.append(getattr(Ticket, key).set(value))

        actions.append(Ticket.version.set(Ticket.version + 1))
        ticket.update(actions=actions)
        ticket.refresh()
        _log_history(ticket)
        return ticket
    except Ticket.DoesNotExist:
        return None


def get_ticket_history(ticket_id: str) -> List[TicketHistory]:
    return list(TicketHistory.query(ticket_id, scan_index_forward=False))
