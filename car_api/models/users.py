# ==============================================================================
# File: car_api/models/users.py
# Description: SQLAlchemy model for user-related data in the Car API.
# ==============================================================================

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from car_api.models import Base

if TYPE_CHECKING:
    from car_api.models.cars import Car


# ==============================================================================
class UserRole(str, Enum):
    """
    Enumeration of user roles.
    """

    USER = 'user'
    ADMIN = 'admin'


# ==============================================================================
class User(Base):
    """
    SQLAlchemy model representing a user in the Car API.

    This model stores authentication, authorization and profile data.
    """

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)

    password: Mapped[str] = mapped_column(nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    # ==============================================================================
    # Relationships
    # ==============================================================================
    cars: Mapped[List['Car']] = relationship(
        'Car',
        back_populates='owner',
        lazy='selectin',
    )
