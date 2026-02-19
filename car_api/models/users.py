# car_api/models/users.py
# ==============================================================================
# File: car_api/models/users.py
# Description: This module defines the SQLAlchemy models for user-related data in the Car API.
# ==============================================================================

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from car_api.models import Base

if TYPE_CHECKING:
    from car_api.models import Car

class User(Base):
    """
    SQLAlchemy model representing a user in the Car API.
    This model defines the structure of the user data stored in the database, including fields for id, username, email, and password.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now()
    )


    # property relationships
    cars: Mapped[List["Car"]] = relationship(
        "Car", 
        back_populates="owner", 
        lazy="selectin"
    )