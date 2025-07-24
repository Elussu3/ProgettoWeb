from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class EventBase(SQLModel):
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    date: datetime = Field(nullable=False)
    location: str = Field(nullable=False, max_length=200)

class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class EventCreate(EventBase):
    pass
