from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class TicketCreate(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Printer not working"})
    description: str = Field(..., json_schema_extra={"example": "The printer on the 2nd floor is out of toner."})
    creator: str = Field(..., json_schema_extra={"example": "john.doe@example.com"})


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, json_schema_extra={"example": "Printer issue"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "The printer is now completely offline."})
    status: Optional[str] = Field(None, json_schema_extra={"example": "IN_PROGRESS"})


class TicketResponse(BaseModel):
    ticket_id: str
    title: str
    description: str
    creator: str
    status: str
    tags: List[str]
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketHistoryResponse(BaseModel):
    ticket_id: str
    version: int
    title: str
    description: str
    creator: str
    status: str
    tags: List[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
