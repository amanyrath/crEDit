"""Database session management"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import get_engine

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get database session context manager
    
    Usage:
        with get_session() as session:
            # Use session
            session.query(Profile).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

