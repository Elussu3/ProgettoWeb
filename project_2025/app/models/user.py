# app/models/user.py
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class UserBase(SQLModel):
    username: str = Field(..., primary_key=True, max_length=50)
    name:     str = Field(..., max_length=100)
    email:    EmailStr

class UserCreate(UserBase):
    """Schema per la creazione di un utente (POST /users)."""
    pass

class UserRead(UserBase):
    """Schema di output per un utente (GET /users e simili)."""
    pass

class User(UserBase, table=True):
    """Tabella User."""
    pass
