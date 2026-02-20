# ==============================================================================
# File: car_api/routers/admin/users.py
# Description: Administrative routes for managing users in the Car API.
# ==============================================================================

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_db_session
from car_api.core.security import require_admin
from car_api.models.users import User, UserRole
from car_api.schemas.users import UserPublicSchema

router = APIRouter(
    prefix='/admin/users',
    tags=['admin - users'],
)


# ==============================================================================
@router.get(
    '/',
    response_model=list[UserPublicSchema],
    summary='Listar usuários',
    description='Lista todos os usuários do sistema. Acesso restrito a administradores.',
)
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(
        None,
        description='Filtrar por username, nome ou email.',
    ),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """
    List all users with optional search and pagination.
    """
    query = select(User)

    if search:
        query = query.where(
            User.username.ilike(f'%{search}%')
            | User.full_name.ilike(f'%{search}%')
            | User.email.ilike(f'%{search}%')
        )

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    users = result.scalars().all()

    return users


# ==============================================================================
@router.get(
    '/{user_id}',
    response_model=UserPublicSchema,
    summary='Obter usuário por ID',
    description='Retorna os dados de um usuário específico. Acesso restrito a administradores.',
)
async def get_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve a specific user by ID.
    """
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    return user


# ==============================================================================
@router.patch(
    '/{user_id}/activate',
    response_model=UserPublicSchema,
    summary='Ativar usuário',
    description='Ativa uma conta de usuário. Acesso restrito a administradores.',
)
async def activate_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Activate a user account.
    """
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    user.is_active = True
    await db.commit()
    await db.refresh(user)

    return user


# ==============================================================================
@router.patch(
    '/{user_id}/deactivate',
    response_model=UserPublicSchema,
    summary='Desativar usuário',
    description='Desativa uma conta de usuário. Acesso restrito a administradores.',
)
async def deactivate_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Deactivate a user account.
    """
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    user.is_active = False
    await db.commit()
    await db.refresh(user)

    return user


# ==============================================================================
@router.patch(
    '/{user_id}/role',
    response_model=UserPublicSchema,
    summary='Alterar papel do usuário',
    description='Altera o papel (USER / ADMIN) de um usuário. Acesso restrito a administradores.',
)
async def change_user_role(
    user_id: int,
    role: UserRole,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Change a user's role.
    """
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    user.role = role
    await db.commit()
    await db.refresh(user)

    return user
