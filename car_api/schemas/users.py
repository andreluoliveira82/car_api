# ==============================================================================
# File: car_api/schemas/users.py
# Description: Pydantic schemas for user-related data in the Car API.
# ==============================================================================

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Optional

from car_api.validators.users import (
    validate_password,
    validate_full_name,
    validate_username
)


# ==============================================================================
class UserBase(BaseModel):
    """
    Base schema for user data shared across multiple operations.
    """
    email: EmailStr
    full_name: str
    username: str
    is_active: Optional[bool] = True

    @field_validator("full_name")
    def validate_full_name_field(cls, value):
        return validate_full_name(value)

    @field_validator("username")
    def validate_username_field(cls, value):
        return validate_username(value)


# ==============================================================================
class UserCreate(UserBase):
    """
    Schema used when creating a new user.
    Includes password validation.
    """
    password: str

    @field_validator("password")
    def validate_password_field(cls, value):
        return validate_password(value)


# ==============================================================================
class UserUpdate(BaseModel):
    """
    Schema for partial updates of user data.
    All fields are optional.
    """
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None    

    @field_validator("password")
    def validate_password_field(cls, value):
        return validate_password(value) if value else value
    
    @field_validator("full_name")
    def validate_full_name_field(cls, value):
        return validate_full_name(value) if value else value
    
    @field_validator("username")
    def validate_username_field(cls, value):
        return validate_username(value) if value else value


# ==============================================================================
class UserPublicSchema(BaseModel):
    """
    Public representation of a user.
    Excludes sensitive fields such as password.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==============================================================================
class UserListPublicSchema(BaseModel):
    """
    Schema for paginated user list responses.
    """
    model_config = ConfigDict(from_attributes=True)

    users: list[UserPublicSchema]
    offset: int
    limit: int
    total: int
