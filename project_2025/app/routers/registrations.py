from typing import List
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.models.registration import Registration
from app.models.user import User
from app.models.event import Event
from app.data.db import SessionDep

router = APIRouter(prefix="/registrations", tags=["Registrations"])

@router.get("/", response_model=List[Registration])
def list_registrations(session: SessionDep):
    return session.exec(select(Registration)).all()

@router.post("/", response_model=Registration, status_code=201)
def create_registration(reg: Registration, session: SessionDep):
    if session.get(User, reg.username) is None:
        raise HTTPException(status_code=404, detail="User not found")
    if session.get(Event, reg.event_id) is None:
        raise HTTPException(status_code=404, detail="Event not found")
    dup = session.exec(
        select(Registration)
        .where(Registration.username == reg.username)
        .where(Registration.event_id == reg.event_id)
    ).first()
    if dup:
        raise HTTPException(status_code=400, detail="Already registered")
    session.add(reg)
    session.commit()
    session.refresh(reg)
    return reg

@router.delete("/", status_code=204)
def delete_registration(
    username: str,
    event_id: int,
    session: SessionDep,
):
    reg_obj = session.get(Registration, (username, event_id))
    if reg_obj is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    session.delete(reg_obj)
    session.commit()
