# ==============================================================================
# File: car_api/models/cars.py
# Description: This module defines the SQLAlchemy models for car-related data in the Car API.
# ==============================================================================

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Text, Numeric, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from car_api.models import Base

if TYPE_CHECKING:
    from car_api.models import User


class Brand(Base):
    """
    SQLAlchemy model representing a car brand in the Car API.
    This model defines the structure of the brand data stored in the database, including fields for id and name.
    """
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now()
    )

    # property relationships
    cars: Mapped[List["Car"]] = relationship(
        "Car",
        back_populates="brand",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class CarType(str, Enum):
    """
    Enum representing the type of a car in the Car API.
    This enum defines the various types of cars that can be categorized in the system, such as sedan, SUV, hatchback, etc.
    """
    HATCH="hatch"
    SEDAN = "sedan"
    SUV = "suv"
    HATCHBACK = "hatchback"
    COUPE = "coupe"
    CONVERTIBLE = "convertible"
    WAGON = "wagon"
    VAN = "van"
    PICKUP = "pickup"
    OTHER = "other"


class CarStatus(str, Enum):
    """Enum representing the status of a car in the Car API."""
    AVAILABLE = "available"
    UNAVAILABLE="unavailable"
    SOLD = "sold"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class CarCondition(str, Enum):
    """Enum representing the condition of a car in the Car API."""
    NEW = "new"
    USED = "used"
    CERTIFIED_PRE_OWNED = "certified pre-owned"


class CarColor(str, Enum):
    """
    Enum representing the color of a car in the Car API.
    This enum defines the various colors that a car can have in the system, such as black, white, silver, etc.  
    """
    BLACK = "black"
    WHITE = "white"
    SILVER = "silver"
    GRAY = "gray"
    RED = "red"
    BLUE = "blue"
    BROWN = "brown"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    OTHER = "other"


class TransmissionType(str, Enum):
    """
    Enum representing the transmission type of a car in the Car API.
    This enum defines the various transmission types that a car can have in the system, such as automatic, manual, semi-automatic, etc.
    """
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SEMI_AUTOMATIC = "semi-automatic"
    CVT = "cvt"


class FuelType(str, Enum):
    """
    Enum representing the fuel type of a car in the Car API.
    This enum defines the various fuel types that a car can use in the system, such as gasoline, diesel, electric, etc.
    """
    GASOLINE = "gasoline"
    ETHANOL = "ethanol"
    FLEX = "flex"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    OTHER = "other"


class Car(Base):
    """
    SQLAlchemy model representing a car in the Car API.
    This model defines the structure of the car data stored in the database, including fields for id, make, model, year, and price.
    """
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    car_type: Mapped[CarType] = mapped_column(String(20), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    factory_year: Mapped[int] = mapped_column(Integer, nullable=False)
    model_year: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[CarColor] = mapped_column(String(20), nullable=False)
    fuel_type: Mapped[FuelType] = mapped_column(String(20), nullable=False)
    transmission: Mapped[TransmissionType] = mapped_column(String(20), default=None)
    condition: Mapped[CarCondition] = mapped_column(String(20), nullable=False)
    status: Mapped[CarStatus] = mapped_column(String(20), default=CarStatus.AVAILABLE)
    mileage: Mapped[int] = mapped_column(Integer, default=0)
    plate: Mapped[str] = mapped_column(String(10), unique=True, default=None, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now()
    )

    # property relationships
    brand: Mapped[Brand] = relationship(
        "Brand", 
        back_populates="cars", 
        lazy="selectin"
    )
    owner: Mapped["User"] = relationship(
        "User", 
        back_populates="cars",
        lazy="selectin"
    )