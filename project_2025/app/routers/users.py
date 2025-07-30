from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, delete

from app.models.user import User, UserCreate, UserRead
from app.data.db import SessionDep

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserRead], summary="List all users")
def list_users(session: SessionDep):
    """
    Restituisce la lista di tutti gli utenti.
    """
    return session.exec(select(User)).all()

@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user"
)
def create_user(
    payload: UserCreate,
    session: SessionDep
):
    """
    Crea un nuovo utente.

    - **username**: identificativo univoco  
    - **name**: nome completo  
    - **email**: indirizzo email valido  
    """
    if session.get(User, payload.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    db_user = User.from_orm(payload)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get(
    "/{username}",
    response_model=UserRead,
    summary="Get a user by username"
)
def get_user(username: str, session: SessionDep):
    """
    Restituisce i dettagli di un singolo utente.

    - **username**: identificativo dell'utente
    """
    user_obj = session.get(User, username)
    if user_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user_obj

@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all users"
)
def delete_all_users(session: SessionDep):
    """
    Elimina tutti gli utenti.
    """
    session.exec(delete(User))
    session.commit()

@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user"
)
def delete_user(username: str, session: SessionDep):
    """
    Elimina l'utente con lo username specificato.
    """
    user_obj = session.get(User, username)
    if user_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    session.delete(user_obj)
    session.commit()