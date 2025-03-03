from sqlalchemy.orm import Session
from typing import Generator

from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
