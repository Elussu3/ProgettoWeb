from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, delete

from app.models.event import Event, EventCreate
from app.data.db import SessionDep
from app.models.registration import RegistrationRequest, Registration
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/", response_model=List[Event], summary="List all events")
def list_events(session: SessionDep):
    """
    Restituisce la lista di tutti gli eventi.
    """
    return session.exec(select(Event)).all()

@router.post(
    "/",
    response_model=Event,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event"
)
def create_event(
    payload: EventCreate,
    session: SessionDep
):
    """
    Crea un nuovo evento.
    """
    new_event = Event.from_orm(payload)
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    return new_event

@router.get("/{event_id}", response_model=Event, summary="Get event by ID")
def get_event(event_id: int, session: SessionDep):
    """
    Restituisce i dettagli dell'evento specificato.
    """
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event

@router.post(
    "/{event_id}/register",
    response_model=Registration,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user to an event"
)
def register_user_to_event(
    event_id: int,
    payload: RegistrationRequest,
    session: SessionDep
):
    """
    Iscrive (o crea) un utente all'evento specificato.
    
    - **username**: identificativo univoco  
    - **name**: nome completo  
    - **email**: indirizzo email valido  
    """
    # 1. Verifica esistenza evento
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    # 2. Recupera o crea utente
    user = session.get(User, payload.username)
    if not user:
        user = User.from_orm(payload)
        session.add(user)
        session.commit()
        session.refresh(user)

    # 3. Evita doppie iscrizioni
    existing = session.exec(
        select(Registration)
        .where(Registration.username == payload.username)
        .where(Registration.event_id == event_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered"
        )

    # 4. Salva la registrazione
    reg = Registration(username=payload.username, event_id=event_id)
    session.add(reg)
    session.commit()
    session.refresh(reg)
    return reg

@router.put(
    "/{event_id}",
    response_model=Event,
    summary="Update an event"
)
def update_event(
    event_id: int,
    payload: EventCreate,
    session: SessionDep
):
    """
    Aggiorna i campi di un evento esistente.
    """
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    event.title = payload.title
    event.description = payload.description
    event.date = payload.date
    event.location = payload.location
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all events"
)
def delete_all_events(session: SessionDep):
    """
    Elimina tutti gli eventi.
    """
    session.exec(delete(Event))
    session.commit()

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an event"
)
def delete_event(event_id: int, session: SessionDep):
    """
    Elimina l'evento con lo ID specificato.
    """
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    session.delete(event)
    session.commit()
