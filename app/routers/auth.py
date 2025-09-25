from fastapi import APIRouter, Depends, HTTPException, status
from app.db.schemas.auth import LoginRequest
from sqlalchemy import select
from app.db import sessions
from app.db.models import Users
from app.db.schemas import users as user_schemas
from app.db.schemas import auth as auth_schemas
from app.utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", summary="Register a new user")
async def register_user(
    payload: user_schemas.UsersCreate,
    db: AsyncSession = Depends(sessions.get_async_session),
) -> str:
    # querying database to check if user already exist
    q = await db.scalars(select(Users).filter(Users.email == payload.email))
    user = q.first()

    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )

    user = Users(
        email=payload.email,
        password=get_password_hash(payload.password),
        name=payload.name,
        group=payload.group,
        gender=payload.gender,
        userType=payload.userType,
    )
    db.add(user)
    await db.commit()

    return "ok"


@router.post(
    "/login",
    summary="Create access and refresh tokens for user",
    response_model=auth_schemas.Token,
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(sessions.get_async_session),
):
    q = await db.scalars(select(Users).filter(Users.email == payload.email))
    user = q.first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    hashed_pass = user.password
    if not verify_password(payload.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    jwt_data = {"sub": user.email}

    return {
        "access_token": create_access_token(jwt_data),
        "refresh_token": create_refresh_token(jwt_data),
    }
