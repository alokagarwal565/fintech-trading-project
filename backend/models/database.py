from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Use in-memory SQLite database for simplicity
DATABASE_URL = "sqlite:///./investment_advisor.db"

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session