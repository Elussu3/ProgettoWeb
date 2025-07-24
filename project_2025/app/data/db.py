# app/data/db.py
from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends
import os
from faker import Faker
from app.config import config
# Import dei modelli per la creazione delle tabelle
from app.models.registration import Registration  # NOQA
from app.models.event import Event               # NOQA
from app.models.user import User                 # NOQA

# 1. Assicuriamoci che esista la cartella "data"
sqlite_file_name = config.root_dir / "data" / "database.db"
os.makedirs(sqlite_file_name.parent, exist_ok=True)

# 2. Stringa di connessione con path assoluto
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
# echo può essere disattivato in produzione via config
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)

def init_database() -> None:
    # 3. Verifichiamo se il DB esisteva già
    db_exists = sqlite_file_name.exists()
    SQLModel.metadata.create_all(engine)
    # 4. Se è un DB nuovo, lanciamo la semina dei dati finti
    if not db_exists:
        seed_fake_data()

def seed_fake_data() -> None:
    """Popola il database con utenti, eventi e registrazioni di esempio."""
    f = Faker("it_IT")
    with Session(engine) as session:
        # — crea 5 utenti
        users = [
            User(
                username=f.unique.user_name(),
                name=f.name(),
                email=f.unique.email()
            )
            for _ in range(5)
        ]
        session.add_all(users)

        # — crea 5 eventi
        events = [
            Event(
                title=f.sentence(nb_words=3).rstrip("."),   # senza il punto finale
                description=f.text(max_nb_chars=50),
                date=f.future_datetime(end_date="+30d"),
                location=f.city()
            )
            for _ in range(5)
        ]
        session.add_all(events)
        session.commit()  # salva utenti + eventi e genera gli ID

        # — registra ogni utente al primo evento
        registrations = [
            Registration(username=u.username, event_id=events[0].id)
            for u in users
        ]
        session.add_all(registrations)
        session.commit()

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
