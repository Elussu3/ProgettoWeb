from typing 	import List
from fastapi 	import APIRouter, HTTPException, status
from sqlmodel 	import select, delete

from app.models.registration 	import Registration, RegistrationRequest
from app.models.user 		import User
from app.models.event 		import Event
from app.data.db 		import SessionDep

router = APIRouter(prefix="/registrations", tags=["Registrations"])

@router.get(
    "/",
    response_model=List[Registration],
    summary="List all registrations"
)
def list_registrations(session: SessionDep):
    """
    Restituisce la lista di tutte le registrazioni.
    """
    return session.exec(select(Registration)).all()

@router.post(
    "/",
    response_model=Registration,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new registration"
)
def create_registration(
    payload: RegistrationRequest,
    session: SessionDep
):
    """
    Crea una nuova registrazione.

    - **username**: identificativo univoco dell'utente  
    - **name**: nome completo dell'utente  
    - **email**: indirizzo email valido dell'utente  
    - **event_id**: identificativo dell'evento a cui iscriversi  
    """
    # 1) Utente esistente?
    if session.get(User, payload.username) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # 2) Evento esistente?
    if session.get(Event, payload.event_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    # 3) Doppia iscrizione?
    dup = session.exec(
        select(Registration)
        .where(Registration.username == payload.username)
        .where(Registration.event_id == payload.event_id)
    ).first()
    if dup:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already registered")
    # 4) Salvo la registrazione
    reg = Registration(username=payload.username, event_id=payload.event_id)
    session.add(reg)
    session.commit()
    session.refresh(reg)
    return reg

@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a registration"
)
def delete_registration(
    username: str,
    event_id: int,
    session: SessionDep
):
    """
    Elimina la registrazione per lo username e l'ID evento specificati.
    """
    session.exec(
        delete(Registration)
        .where(Registration.username == username)
        .where(Registration.event_id == event_id)
    )
    session.commit()
