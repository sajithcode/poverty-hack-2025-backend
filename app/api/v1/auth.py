from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.db import get_db
from app.core.deps import (
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
    generate_uuid
)
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserRegister, UserLogin, Token, User as UserSchema, UserMe

router = APIRouter()


@router.post("/register", response_model=UserSchema)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify role exists
    role_result = await db.execute(select(Role).where(Role.id == user_data.role_id))
    if not role_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role ID"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        uuid=generate_uuid(),
        role_id=user_data.role_id,
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access token."""
    # Get user by email
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.uuid}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserMe)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get current user information."""
    # Get role name
    role_result = await db.execute(select(Role).where(Role.id == current_user.role_id))
    role = role_result.scalar_one_or_none()
    
    user_data = UserMe.model_validate(current_user)
    user_data.role_name = role.name if role else None
    
    return user_data