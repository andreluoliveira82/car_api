# ==============================================================================
# File: car_api/schemas/brands.py
# Description: Pydantic schemas for brand-related data in the Car API.
# ==============================================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from car_api.validators.cars import (
    validate_brand_description,
    validate_brand_name,
)


# ==============================================================================
class BrandCreateSchema(BaseModel):
    """
    Schema used to create a new brand.
    Intended for administrative use.
    """

    name: str = Field(..., example='Toyota')
    description: Optional[str] = Field(
        None,
        example='Uma marca japonesa conhecida por sua confiabilidade.',
    )

    @field_validator('name')
    def validate_name(cls, value):
        return validate_brand_name(value)

    @field_validator('description')
    def validate_description(cls, value):
        return validate_brand_description(value) if value else value


# ==============================================================================
class BrandUpdateSchema(BaseModel):
    """
    Schema used to update an existing brand.
    Intended for administrative use.
    """

    name: Optional[str] = Field(None, example='Toyota')
    description: Optional[str] = Field(
        None,
        example='Uma marca japonesa conhecida por sua confiabilidade.',
    )

    @field_validator('name')
    def validate_name(cls, value):
        return validate_brand_name(value) if value else value

    @field_validator('description')
    def validate_description(cls, value):
        return validate_brand_description(value) if value else value


# ==============================================================================
class BrandPublicSchema(BaseModel):
    """
    Public representation of a brand.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==============================================================================
class BrandListPublicSchema(BaseModel):
    """
    Schema for paginated brand list responses.
    """

    model_config = ConfigDict(from_attributes=True)

    brands: list[BrandPublicSchema]
    offset: int
    limit: int
    total: int
