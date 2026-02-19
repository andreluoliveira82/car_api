# car_api/models/base.py

# ==============================================================================
# File: car_api/models/base.py
# Description: This module defines the base model classes for the Car API.
# ==============================================================================

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models in the Car API.
    This class serves as the foundation for all database models, providing common functionality and configuration.
    """
    pass