# ==============================================================================
# File: car_api/schemas/users.py
# Description: Pydantic schemas for user-related data in the Car API.
# ==============================================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from car_api.validators.users import (
    validate_full_name,
    validate_password,
    validate_username,
)


# ==============================================================================
class UserBase(BaseModel):
    """
    Base schema for shared user attributes.
    """

    email: EmailStr
    full_name: str
    username: str

    @field_validator('full_name')
    def validate_full_name_field(cls, value):
        return validate_full_name(value)

    @field_validator('username')
    def validate_username_field(cls, value):
        return validate_username(value)


# ==============================================================================
class UserCreate(UserBase):
    """
    Schema used when creating a new user.
    """

    password: str

    @field_validator('password')
    def validate_password_field(cls, value):
        return validate_password(value)


# ==============================================================================
class UserUpdate(BaseModel):
    """
    Schema for updating the authenticated user's own data.
    All fields are optional.
    """

    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator('password')
    def validate_password_field(cls, value):
        return validate_password(value) if value else value

    @field_validator('full_name')
    def validate_full_name_field(cls, value):
        return validate_full_name(value) if value else value

    @field_validator('username')
    def validate_username_field(cls, value):
        return validate_username(value) if value else value


# ==============================================================================
class UserPublicSchema(BaseModel):
    """
    Public representation of a user.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
