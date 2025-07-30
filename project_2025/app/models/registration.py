# app/models/registration.py
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class RegistrationRequest(SQLModel):
    """Schema di input per POST /events/{id}/register."""
    username: str     = Field(..., max_length=50)
    name:     str     = Field(..., max_length=100)
    email:    EmailStr

class Registration(SQLModel, table=True):
    """Tabella Registration (solo chiavi esterne)."""
    username: str = Field(
        foreign_key="user.username",
        primary_key=True,
        max_length=50
    )
    event_id: int = Field(
        foreign_key="event.id",
        primary_key=True
    )
