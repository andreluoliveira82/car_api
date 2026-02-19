# ==============================================================================
# File: car_api/validators/cars.py
# Description: Validation logic for car-related data in the Car API.
# ==============================================================================

from datetime import datetime
import re

from car_api.core.settings import settings


# ============================
# Configurable domain constants
# ============================

MIN_FACTORY_YEAR = settings.MIN_FACTORY_YEAR
MAX_FUTURE_YEAR = settings.MAX_FUTURE_YEAR
MAX_PRICE = settings.MAX_PRICE
MAX_MILEAGE = settings.MAX_MILEAGE
MAX_BRAND_DESCRIPTION = settings.MAX_BRAND_DESCRIPTION


# ============================
# Brand Validators
# ============================

def validate_brand_name(value: str) -> str:
    value = value.strip()

    match value:
        case "":
            raise ValueError("O nome da marca não pode estar vazio.")
        case _ if len(value) < 2:
            raise ValueError("O nome da marca deve ter pelo menos 2 caracteres.")
        case _ if len(value) > 50:
            raise ValueError("O nome da marca deve ter no máximo 50 caracteres.")

    # Permite letras, números, espaços e hífens
    if not re.match(r"^[A-Za-z0-9\s\-]+$", value):
        raise ValueError("O nome da marca deve conter apenas letras, números, espaços e hífens.")

    return value.strip()


def validate_brand_description(value: str) -> str:
    if len(value) > MAX_BRAND_DESCRIPTION:
        raise ValueError(f"A descrição deve ter no máximo {MAX_BRAND_DESCRIPTION} caracteres.")
    return value.strip()


# ============================
# Car Model Validators
# ============================

def validate_car_model(value: str) -> str:
    value = value.strip()

    match value:
        case "":
            raise ValueError("O modelo do carro não pode estar vazio.")
        case _ if len(value) < 2:
            raise ValueError("O modelo deve ter pelo menos 2 caracteres.")
        case _ if len(value) > 50:
            raise ValueError("O modelo deve ter no máximo 50 caracteres.")

    # Permite letras, números, espaços e hífens
    if not re.match(r"^[A-Za-z0-9\s\-]+$", value):
        raise ValueError("O modelo deve conter apenas letras, números, espaços e hífens.")

    return value.strip()


# ============================
# Year Validators
# ============================

def validate_car_factory_year(value: int) -> int:
    current_year = datetime.now().year

    if value < MIN_FACTORY_YEAR:
        raise ValueError(f"O ano de fabricação deve ser a partir de {MIN_FACTORY_YEAR}.")
    if value > current_year + MAX_FUTURE_YEAR:
        raise ValueError(f"O ano de fabricação não pode ultrapassar {current_year + MAX_FUTURE_YEAR}.")

    return value


def validate_car_model_year(value: int, factory_year: int) -> int:
    current_year = datetime.now().year

    if value < factory_year:
        raise ValueError("O ano do modelo não pode ser anterior ao ano de fabricação.")
    if value > current_year + MAX_FUTURE_YEAR:
        raise ValueError(f"O ano do modelo não pode ultrapassar {current_year + MAX_FUTURE_YEAR}.")

    return value


# ============================
# Price & Mileage Validators
# ============================

def validate_car_price(value: float) -> float:
    if value < 0:
        raise ValueError("O preço não pode ser negativo.")
    if value > MAX_PRICE:
        raise ValueError(f"O preço deve ser no máximo {MAX_PRICE:,}.")
    return value


def validate_car_mileage(value: int) -> int:
    if value < 0:
        raise ValueError("A quilometragem não pode ser negativa.")
    if value > MAX_MILEAGE:
        raise ValueError(f"A quilometragem deve ser no máximo {MAX_MILEAGE:,}.")
    return value


# ============================
# License Plate Validator (BR)
# ============================

def validate_car_plate(value: str) -> str:
    """
    Valida placas brasileiras nos dois padrões:
    - Antigo: AAA-0000
    - Mercosul: AAA0A00
    """

    value = value.replace("-", "").upper().strip()

    # Padrão antigo: 3 letras + 4 números
    old_pattern = r"^[A-Z]{3}[0-9]{4}$"

    # Padrão Mercosul: 3 letras + 1 número + 1 letra + 2 números
    mercosul_pattern = r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$"

    if not (re.match(old_pattern, value) or re.match(mercosul_pattern, value)):
        raise ValueError("Placa inválida. Aceitos: padrão antigo (AAA0000) ou Mercosul (AAA0A00).")

    return value.upper()
