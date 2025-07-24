from typing import List
from fastapi import APIRouter, HTTPException
from sqlmodel import select, delete

from app.models.event import Event, EventCreate
from app.data.db import SessionDep
from app.models.registration import Registration
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/", response_model=List[Event])
def list_events(session: SessionDep):
    return session.exec(select(Event)).all()

@router.post("/", response_model=Event, status_code=201)
def create_event(payload: EventCreate, session: SessionDep):
    new_event = Event.from_orm(payload)
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    return new_event

@router.get("/{event_id}", response_model=Event)
def get_event(event_id: int, session: SessionDep):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/{event_id}/register", response_model=Registration, status_code=201)
def register_user_to_event(
    event_id: int,
    reg_data: Registration,
    session: SessionDep,
):
    if session.get(Event, event_id) is None:
        raise HTTPException(status_code=404, detail="Event not found")
    user = session.get(User, reg_data.username)
    if user is None:
        user = User(username=reg_data.username, name=reg_data.username, email="")
        session.add(user)
        session.commit()
    dup = session.exec(
        select(Registration)
        .where(Registration.username == reg_data.username)
        .where(Registration.event_id == event_id)
    ).first()
    if dup:
        raise HTTPException(status_code=400, detail="Already registered")

    registration = Registration(username=reg_data.username, event_id=event_id)
    session.add(registration)
    session.commit()
    session.refresh(registration)
    return registration

@router.put("/{event_id}", response_model=Event)
def update_event(
    event_id: int,
    payload: EventCreate,
    session: SessionDep,
):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    event.title = payload.title
    event.description = payload.description
    event.date = payload.date
    event.location = payload.location
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.delete("/", status_code=204)
def delete_all_events(session: SessionDep):
    session.exec(delete(Event))
    session.commit()

@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, session: SessionDep):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    session.delete(event)
    session.commit()
