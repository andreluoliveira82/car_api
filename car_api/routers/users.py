# ==============================================================================
# File: car_api/routers/users.py
# Description: FastAPI router for user-related operations in the Car API.
#
# Design notes (production-minded):
# - Public: user registration (POST /users)
# - Protected: self-service profile management (GET/PUT/DELETE /users/me)
# - No public user listing or lookup-by-id (prevents user enumeration and data leakage)
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_db_session
from car_api.core.security import get_current_user, get_password_hash
from car_api.models.users import User
from car_api.schemas.users import UserCreate, UserPublicSchema, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])


# ==============================================================================
@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary='Criar um novo usuário',
    description='Permite que visitantes se cadastrem no sistema.',
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session),
) -> UserPublicSchema:
    """
    Create a new user.

    This endpoint is public by design to allow new registrations.
    It enforces unique username and email and stores a hashed password.
    """
    username_exists = await db.scalar(
        select(exists().where(User.username == user.username))
    )
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username não disponível. Já existe um usuário cadastrado com este username.',
        )

    email_exists = await db.scalar(select(exists().where(User.email == user.email)))
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email já existe. Já existe um usuário cadastrado com este email.',
        )

    db_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        password=get_password_hash(user.password),
        is_active=True,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


# ==============================================================================
@router.get(
    path='/me',
    status_code=status.HTTP_200_OK,
    response_model=UserPublicSchema,
    summary='Obter dados do usuário autenticado',
    description='Retorna o perfil do usuário atualmente autenticado.',
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserPublicSchema:
    """
    Return the authenticated user's profile.
    """
    return current_user


# ==============================================================================
@router.put(
    path='/me',
    status_code=status.HTTP_200_OK,
    response_model=UserPublicSchema,
    summary='Atualizar dados do usuário autenticado',
    description='Atualiza parcialmente os dados do próprio usuário (inclui troca de senha).',
)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> UserPublicSchema:
    """
    Update the authenticated user's profile.

    Security:
    - Only the authenticated user can update their own data.
    - Username/email uniqueness is enforced excluding the current user.
    - Password is hashed before persisting.
    """
    # Validate username uniqueness (excluding current user)
    if user_update.username and user_update.username != current_user.username:
        username_exists = await db.scalar(
            select(
                exists().where(
                    User.username == user_update.username,
                    User.id != current_user.id,
                )
            )
        )
        if username_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username já está em uso.',
            )

    # Validate email uniqueness (excluding current user)
    if user_update.email and user_update.email != current_user.email:
        email_exists = await db.scalar(
            select(
                exists().where(
                    User.email == user_update.email,
                    User.id != current_user.id,
                )
            )
        )
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email já está em uso.',
            )

    # Update password separately (hashing)
    if user_update.password:
        current_user.password = get_password_hash(user_update.password)

    # Update remaining fields
    update_data = user_update.model_dump(exclude_unset=True, exclude={'password'})
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return current_user


# ==============================================================================
@router.delete(
    path='/me',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Excluir a própria conta',
    description='Remove a conta do usuário autenticado.',
)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete the authenticated user's account.
    """
    await db.delete(current_user)
    await db.commit()
