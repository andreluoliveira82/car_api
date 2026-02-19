# ==============================================================================
# File: car_api/schemas/cars.py
# Description: Pydantic schemas for car-related data in the Car API.
# ==============================================================================

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from car_api.models.cars import (
    CarColor, CarCondition, CarStatus, CarType, FuelType, TransmissionType
)
from car_api.schemas.brands import BrandPublicSchema
from car_api.schemas.users import UserPublicSchema
from car_api.validators.cars import (
    validate_car_model,
    validate_car_factory_year,
    validate_car_mileage,
    validate_car_model_year,
    validate_car_plate,
    validate_car_price
)


# ==============================================================================
class CarSchema(BaseModel):
    """
    Schema for creating a new car.
    """
    car_type: CarType = Field(..., example="suv")
    model: str = Field(..., example="Corolla Cross")
    factory_year: int = Field(..., example=2025)
    model_year: int = Field(..., example=2026)
    color: CarColor = Field(..., example="white")
    fuel_type: FuelType = Field(..., example="flex")
    transmission: TransmissionType = Field(..., example="automatic")
    condition: CarCondition = Field(..., example="used")
    status: CarStatus = Field(default=CarStatus.AVAILABLE, example="available")
    mileage: int = Field(..., example=1000)
    plate: str = Field(..., example="ABC0D12")
    price: Decimal = Field(..., example=105999.99)
    description: Optional[str] = Field(None, example="Carro confortável e seguro. Bom estado.")
    brand_id: int = Field(..., example=1)
    owner_id: int = Field(..., example=3)

    @field_validator("model")
    def validate_model(cls, value):
        return validate_car_model(value)

    @field_validator("plate")
    def validate_plate(cls, value):
        return validate_car_plate(value)

    @field_validator("factory_year")
    def validate_factory_year(cls, value):
        return validate_car_factory_year(value)

    @field_validator("mileage")
    def validate_mileage(cls, value):
        return validate_car_mileage(value)

    @field_validator("price")
    def validate_price(cls, value):
        return validate_car_price(value)

    @model_validator(mode="after")
    def validate_years(self):
        validate_car_model_year(self.model_year, self.factory_year)
        return self



# ==============================================================================
class CarUpdateSchema(BaseModel):
    """
    Schema for partial updates of car data.
    All fields are optional.
    """
    car_type: Optional[CarType] = Field(None, example="suv")
    model: Optional[str] = Field(None, example="Corolla Cross")
    factory_year: Optional[int] = Field(None, example=2025)
    model_year: Optional[int] = Field(None, example=2026)
    color: Optional[CarColor] = Field(None, example="white")
    fuel_type: Optional[FuelType] = Field(None, example="flex")
    transmission: Optional[TransmissionType] = Field(None, example="automatic")
    condition: Optional[CarCondition] = Field(None, example="used")
    status: Optional[CarStatus] = Field(None, example="available")
    mileage: Optional[int] = Field(None, example=15000)
    plate: Optional[str] = Field(None, example="ABC0D12")
    price: Optional[Decimal] = Field(None, example=105999.99)
    description: Optional[str] = Field(None, example="Carro revisado recentemente.")
    brand_id: Optional[int] = Field(None, example=1)
    owner_id: Optional[int] = Field(None, example=3)

    @field_validator("model")
    def validate_model(cls, value):
        return validate_car_model(value) if value else value

    @field_validator("plate")
    def validate_plate(cls, value):
        return validate_car_plate(value) if value else value

    @field_validator("factory_year")
    def validate_factory_year(cls, value):
        return validate_car_factory_year(value) if value else value

    @field_validator("mileage")
    def validate_mileage(cls, value):
        return validate_car_mileage(value) if value else value

    @field_validator("price")
    def validate_price(cls, value):
        return validate_car_price(value) if value else value

    @model_validator(mode="after")
    def validate_years(self):
        # Só valida se ambos forem enviados
        if self.model_year and self.factory_year:
            validate_car_model_year(self.model_year, self.factory_year)
        return self


# ==============================================================================
class CarPublicSchema(BaseModel):
    """
    Public representation of a car.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., example=10)
    car_type: CarType = Field(..., example="suv")
    model: str = Field(..., example="Corolla Cross")
    factory_year: int = Field(..., example=2025)
    model_year: int = Field(..., example=2026)
    color: CarColor = Field(..., example="white")
    fuel_type: FuelType = Field(..., example="flex")
    transmission: TransmissionType = Field(..., example="automatic")
    condition: CarCondition = Field(..., example="used")
    status: CarStatus = Field(..., example="available")
    mileage: int = Field(..., example=15000)
    plate: str = Field(..., example="ABC0D12")
    price: Decimal = Field(..., example=105999.99)
    description: Optional[str] = Field(None, example="Carro confortável e seguro.")
    brand_id: int = Field(..., example=1)
    owner_id: int = Field(..., example=3)
    created_at: datetime = Field(..., example="2025-01-10T14:32:00")
    updated_at: datetime = Field(..., example="2025-02-01T09:15:00")

    # Relações
    brand: Optional[BrandPublicSchema] = None
    owner: Optional[UserPublicSchema] = None


# ==============================================================================
class CarListPublicSchema(BaseModel):
    """
    Schema for paginated car list responses.
    """
    model_config = ConfigDict(from_attributes=True)

    cars: list[CarPublicSchema]
    offset: int
    limit: int
    total: int
