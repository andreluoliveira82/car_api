# ==============================================================================
# File: car_api/schemas/brans.py
# Description: Pydantic schemas for brand-related data in the Car API.
# ==============================================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from car_api.validators.cars import (
    validate_brand_name,
    validate_brand_description
)

# ==============================================================================
class BrandSchema(BaseModel):
    name: str = Field(..., example="Toyota")
    description: Optional[str] = Field(None, example="Uma marca japonesa conhecida por sua confiabilidade.")
    is_active: Optional[bool] = True

    @field_validator("name")
    def validate_name(cls, value):
        return validate_brand_name(value)

    @field_validator("description")
    def validate_description(cls, value):
        return validate_brand_description(value) if value else value


# ==============================================================================
class BrandUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, example="Toyota")
    description: Optional[str] = Field(None, example="Uma marca japonesa conhecida por sua confiabilidade.")
    is_active: Optional[bool] = None

    @field_validator("name")
    def validate_name(cls, value):
        return validate_brand_name(value) if value else value

    @field_validator("description")
    def validate_description(cls, value):
        return validate_brand_description(value) if value else value


# ==============================================================================
class BrandPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ==============================================================================
class BrandListPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    brands: list[BrandPublicSchema]
    offset: int
    limit: int
    total: int
