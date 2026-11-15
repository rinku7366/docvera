from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserCreate, Token


def register_user(data: UserCreate, db: Session) -> User:
    """
    Create a new user account.
    Checks for duplicate email first — returning a clear 409 error
    rather than letting the database unique constraint bubble up as a 500.
    """
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(email: str, password: str, db: Session) -> Token:
    """
    Verify credentials and return a JWT token on success.
    We deliberately give the same error message for wrong email and wrong
    password to avoid leaking whether an email is registered.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token({"user_id": user.id})
    return Token(access_token=token)
