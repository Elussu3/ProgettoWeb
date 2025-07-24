from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    username: str = Field(primary_key=True, max_length=50)
    name: str = Field(nullable=False, max_length=100)
    email: str = Field(nullable=False, max_length=200)
