import os
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    UTCDateTimeAttribute,
    ListAttribute,
)

DYNAMODB_REGION = os.getenv("DYNAMODB_REGION", "us-east-1")
DYNAMODB_HOST = os.getenv("DYNAMODB_HOST", None)
TICKETS_TABLE_NAME = "Helpdesk-Tickets"
TICKETS_HISTORY_TABLE_NAME = "Helpdesk-TicketsHistory"


class Ticket(Model):

    class Meta:
        table_name = TICKETS_TABLE_NAME
        region = DYNAMODB_REGION
        host = DYNAMODB_HOST
        write_capacity_units = 1
        read_capacity_units = 1

    ticket_id = UnicodeAttribute(hash_key=True)
    title = UnicodeAttribute()
    description = UnicodeAttribute()
    creator = UnicodeAttribute()
    status = UnicodeAttribute(default="OPEN")
    tags = ListAttribute(default=list)
    version = NumberAttribute(default=1)
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        super().save(*args, **kwargs)


class TicketHistory(Model):


    class Meta:
        table_name = TICKETS_HISTORY_TABLE_NAME
        region = DYNAMODB_REGION
        host = DYNAMODB_HOST
        write_capacity_units = 1
        read_capacity_units = 1

    ticket_id = UnicodeAttribute(hash_key=True)
    version = NumberAttribute(range_key=True)
    title = UnicodeAttribute()
    description = UnicodeAttribute()
    creator = UnicodeAttribute()
    status = UnicodeAttribute()
    tags = ListAttribute(default=list)
    timestamp = UTCDateTimeAttribute(default=datetime.utcnow)
