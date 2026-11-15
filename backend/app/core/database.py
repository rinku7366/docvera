from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# SQLAlchemy 2.0-style engine.
# check_same_thread=False is required for SQLite when used with FastAPI
# because FastAPI may share a connection across threads in async context.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Set to True temporarily to debug SQL queries
)

# Session factory — each request gets its own session, closed after.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    All ORM models inherit from this Base.
    Why: using the new DeclarativeBase style from SQLAlchemy 2.0
    for cleaner type annotations.
    """
    pass


def get_db():
    """
    FastAPI dependency that yields a database session per request
    and ensures it is always closed, even if an exception occurs.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables defined by ORM models.
    Called once at application startup in main.py.
    Why: keeps schema management simple for a demo project.
    """
    # Import all models here so SQLAlchemy knows about them before create_all
    import app.models.user        # noqa: F401
    import app.models.document    # noqa: F401
    import app.models.query       # noqa: F401
    import app.models.verification  # noqa: F401
    import app.models.translation # noqa: F401
    import app.models.audit       # noqa: F401
    Base.metadata.create_all(bind=engine)
