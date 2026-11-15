from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.features.auth.dependencies import get_current_user
from app.features.auth.service import register_user, authenticate_user
from app.models.user import UserCreate, UserRead, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account. Returns the created user (without password)."""
    user = register_user(data, db)
    return user


@router.post("/login", response_model=Token)
def login(data: UserCreate, db: Session = Depends(get_db)):
    """
    Authenticate with email + password.
    Returns a JWT bearer token to use in subsequent requests.
    """
    return authenticate_user(data.email, data.password, db)


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
