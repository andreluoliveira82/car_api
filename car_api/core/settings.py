# car_api/core/settings.py
# ==============================================================================
# File: car_api/core/settings.py
# Description: This module defines the configuration settings for the Car API, including database connection details and other application settings.
# ==============================================================================

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuration settings for the Car API application.
    This class uses Pydantic's BaseSettings to manage application configuration, including database connection details and other settings.
    """
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8"
    )

    # Database settings
    DATABASE_URL: str

    # Domain-specific settings
    MIN_FACTORY_YEAR : int
    MAX_FUTURE_YEAR : int
    MAX_PRICE : int
    MAX_MILEAGE : int
    MAX_BRAND_DESCRIPTION : int

# Instancia global de configurações
settings = Settings()