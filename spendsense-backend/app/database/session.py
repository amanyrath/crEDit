"""Database session management"""

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import get_engine

# Lazy session factory - created on first access
_session_factory: Optional[sessionmaker] = None


def _get_session_factory() -> sessionmaker:
    """Get or create the session factory (lazy initialization)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _session_factory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get database session context manager
    
    Usage:
        with get_session() as session:
            # Use session
            session.query(Profile).all()
    """
    SessionLocal = _get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

