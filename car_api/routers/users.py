# car_api/routers/users.py

# ==============================================================================
# File: car_api/routers/users.py
# Description: This module defines the API endpoints for user-related operations in the Car API.
# ==============================================================================

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from car_api.core.database import get_db_session
from car_api.core.security import get_password_hash
from car_api.models.users import User
from car_api.schemas.users import (
    UserBase,
    UserCreate,
    UserListPublicSchema,
    UserPublicSchema,
    UserUpdate
)

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

#=============================================================================
@router.post(
        path="/", 
        status_code=status.HTTP_201_CREATED,
        response_model=UserPublicSchema,
        summary="Criar um novo usuário",
        description="Este endpoint permite criar um novo usuário fornecendo os dados necessários."
    )
async def create_user(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db_session)
) -> UserPublicSchema:
    """
    Endpoint to create a new user.
    Args:
        user (UserCreate): The user data to create.
        db (AsyncSession): The database session.
    Returns:
        UserPublicSchema: The created user data (excluding sensitive information).
    """
    # validate if user with the same email or username already exists
    username_exists = await db.scalar(
        select(exists().where(User.username == user.username))
    )

    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usename não disponível. Já existe um usuário cadastrado com este username.",
        )

    email_exists = await db.scalar(
        select(exists().where(User.email == user.email))
    )

    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já existe. Já existe um usuário cadastrado com este email."
        )

    db_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        password=get_password_hash(user.password),
        is_active=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user

#=============================================================================
@router.get(
        path="/{user_id}",
        status_code=status.HTTP_200_OK,
        response_model=UserPublicSchema,
        summary="Obter um usuário específico",
        description="Este endpoint permite obter os dados de um usuário específico fornecendo o ID do usuário."
    )
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_session)) -> UserPublicSchema:
    """Endpoint to get a specific user.
    Args:
        user_id (int): The ID of the user to retrieve.
        db (AsyncSession): The database session.
    Returns:
        UserPublicSchema: The user data (excluding sensitive information).
    """
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    return db_user

#=============================================================================
@router.get(
        path="/", 
        status_code=status.HTTP_200_OK,
        response_model=UserListPublicSchema,
        summary="Listar todos os usuários",
        description="Este endpoint retorna uma lista de todos os usuários cadastrados, excluindo informações sensíveis."
    )
async def list_users(
    offset: int = Query(0, ge=0, description="Número de itens a pular antes de começar a coletar os resultados."),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de itens a retornar."),
    search: Optional[str] = Query(None, description="Termo de busca para filtrar usuários por nome, username ou email."),
    db: AsyncSession = Depends(get_db_session)
) -> UserListPublicSchema:
    """
    Endpoint to list all users.
    Args:
        db (AsyncSession): The database session.
    Returns:
        UserListPublicSchema: A list of all users (excluding sensitive information).
    """
    query = select(User)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            (User.username.ilike(search_term)) |
            (User.full_name.ilike(search_term)) |
            (User.email.ilike(search_term))
        )
    query = query.offset(offset).limit(limit)
    
    users = await db.execute(query)
    db_users = users.scalars().all()

    if not db_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuário encontrado.",
        )

    return {
        "users": db_users,
        "offset": offset,
        "limit": limit,
        "total": len(db_users)
    }


#=============================================================================
@router.put(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublicSchema,
    summary="Atualizar um usuário existente",
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db_session)
) -> UserPublicSchema:

    db_user = await db.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    # Validar username
    if user_update.username and user_update.username != db_user.username:
        username_exists = await db.scalar(
            select(
                exists().where(
                    User.username == user_update.username,
                    User.id != user_id
                )
            )
        )
        if username_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já está em uso.",
            )

    # Validar email
    if user_update.email and user_update.email != db_user.email:
        email_exists = await db.scalar(
            select(
                exists().where(
                    User.email == user_update.email,
                    User.id != user_id
                )
            )
        )
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso.",
            )

    # Atualizar senha separadamente
    if user_update.password:
        db_user.password = get_password_hash(user_update.password)

    # Atualizar demais campos
    update_data = user_update.model_dump(
        exclude_unset=True,
        exclude={"password"}
    )

    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)

    return db_user


#=============================================================================
@router.delete(
        path="/{user_id}", 
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Deletar um usuário",
        description="Este endpoint permite deletar um usuário existente fornecendo o ID do usuário."
    )
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db_session)) -> None:
    """Endpoint to delete an existing user.
    Args:
        user_id (int): The ID of the user to delete.
        db (AsyncSession): The database session.
    Returns:
        None: No content is returned upon successful deletion.
    """
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.",)

    await db.delete(db_user)
    await db.commit()

    return None
