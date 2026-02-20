# ==============================================================================
# File: car_api/schemas/auth.py
# Description: Pydantic schemas for authentication and authorization.
# ==============================================================================

from pydantic import BaseModel, EmailStr, Field, field_validator

from car_api.validators.users import validate_email, validate_password


# ==============================================================================
class TokenResponse(BaseModel):
    """
    Schema returned after successful authentication.
    """

    access_token: str = Field(..., example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
    token_type: str = Field(default='bearer', example='bearer')


# ==============================================================================
class TokenPairResponse(BaseModel):
    """
    Schema returned after successful login.
    """

    access_token: str = Field(..., example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
    refresh_token: str = Field(..., example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
    token_type: str = Field(default='bearer', example='bearer')


# ==============================================================================
class LoginRequest(BaseModel):
    """
    Schema used for user login.
    """

    email: EmailStr = Field(..., example='user@example.com')
    password: str = Field(..., example='StrongPass123')

    @field_validator('email')
    def validate_email_field(cls, value):
        return validate_email(value)

    @field_validator('password')
    def validate_password_field(cls, value):
        return validate_password(value)


# ==============================================================================
class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
