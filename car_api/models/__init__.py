# ==============================================================================
# car_api/models/__init__.py
# Description: This module defines the SQLAlchemy models for the Car API, including the User and Car models, as well as the Brand model and related enums for car types, status, and condition.
# The models define the structure of the data stored in the database and the relationships between different entities in the Car API.
# Created by André Luiz de Almeida - 2024-06-17
# Car API - FastAPI project
# The models define the structure of the data stored in the database and the relationships between different entities in the Car API.
# ==============================================================================

from car_api.models.base import Base
from car_api.models.cars import Brand, Car
from car_api.models.users import User

__all__ = ['Base', 'User', 'Brand', 'Car']
