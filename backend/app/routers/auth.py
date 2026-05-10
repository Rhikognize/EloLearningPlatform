from __future__ import annotations
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.dependencies import get_current_user
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])


async def _issue_tokens(
    user: User,
    response: Response,
    db: AsyncSession,
) -> TokenResponse:
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    refresh_token_hash = hash_refresh_token(refresh_token)

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    stmt = pg_insert(RefreshToken).values(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=expires_at,
        is_revoked=False,
    )
    await db.execute(stmt)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    existing_username = await db.scalar(
        select(User).where(User.username == body.username)
    )
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Acest username este deja folosit"
        )

    existing_email = await db.scalar(
        select(User).where(User.email == body.email)
    )
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Acest email este deja înregistrat"
        )

    new_user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(new_user)
    await db.flush()

    return await _issue_tokens(new_user, response, db)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(
        select(User).where(User.email == body.email)
    )

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email sau parolă incorecte"
        )

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email sau parolă incorecte"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contul este dezactivat"
        )

    return await _issue_tokens(user, response, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token lipsește"
        )

    token_hash = hash_refresh_token(refresh_token)
    db_token = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalid sau expirat"
        )

    user = await db.get(User, db_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizatorul nu există sau este dezactivat"
        )

    db_token.is_revoked = True

    return await _issue_tokens(user, response, db)


@router.post("/logout", status_code=200)
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    if refresh_token:
        token_hash = hash_refresh_token(refresh_token)
        db_token = await db.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        if db_token:
            db_token.is_revoked = True

    response.delete_cookie(key="refresh_token")
    return {"message": "Deconectat cu succes"}
