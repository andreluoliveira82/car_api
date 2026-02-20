# ==============================================================================
# File: car_api/routers/auth.py
# Description: Authentication routes for the Car API.
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_db_session
from car_api.core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from car_api.models.users import User
from car_api.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenPairResponse,
    TokenResponse,
)

router = APIRouter(prefix='/auth', tags=['authentication'])


# ==============================================================================
@router.post(
    '/login',
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    summary='Autenticar usuário',
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    user = await authenticate_user(
        email=credentials.email,
        password=credentials.password,
        db=db,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email ou senha inválidos',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return TokenPairResponse(
        access_token=create_access_token(
            subject=str(user.id),
            role=user.role.value,
        ),
        refresh_token=create_refresh_token(subject=str(user.id)),
        token_type='bearer',
    )


# ==============================================================================
@router.post(
    '/refresh',
    response_model=TokenResponse,
    summary='Renovar access token',
    description='Gera um novo access token a partir de um refresh token válido.',
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    payload = verify_token(data.refresh_token, expected_type='refresh')

    user_id = payload.get('sub')

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
        )

    new_access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
    )

    return TokenResponse(access_token=new_access_token, token_type='bearer')
