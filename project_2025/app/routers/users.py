from typing import List
from fastapi import APIRouter, HTTPException
from sqlmodel import select, delete

from app.models.user import User
from app.data.db import SessionDep

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[User])
def list_users(session: SessionDep):
    return session.exec(select(User)).all()

@router.post("/", response_model=User, status_code=201)
def create_user(user: User, session: SessionDep):
    if session.get(User, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/{username}", response_model=User)
def get_user(username: str, session: SessionDep):
    user_obj = session.get(User, username)
    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

@router.delete("/", status_code=204)
def delete_all_users(session: SessionDep):
    session.exec(delete(User))
    session.commit()

@router.delete("/{username}", status_code=204)
def delete_user(username: str, session: SessionDep):
    user_obj = session.get(User, username)
    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user_obj)
    session.commit()
