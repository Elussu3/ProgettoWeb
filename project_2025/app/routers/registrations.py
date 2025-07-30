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
