# ==============================================================================
# File: car_api/validators/users.py
# Description: Validation logic for user-related data in the Car API.
# ==============================================================================

import re

from pydantic import EmailStr

# ============================
# Password Validator
# ============================


def validate_password(value: str) -> str:
    value = value.strip()

    match value:
        case '':
            raise ValueError('A senha não pode estar vazia.')
        case _ if len(value) < 6:
            raise ValueError('A senha deve ter pelo menos 6 caracteres.')
        case _ if len(value) > 15:
            raise ValueError('A senha deve ter no máximo 15 caracteres.')

    if not any(char.isdigit() for char in value):
        raise ValueError('A senha deve conter pelo menos um número.')

    if not any(char.isalpha() for char in value):
        raise ValueError('A senha deve conter pelo menos uma letra.')

    return value


# ============================
# Full Name Validator
# ============================


def validate_full_name(value: str) -> str:
    value = value.strip()

    match value:
        case '':
            raise ValueError('O nome completo não pode estar vazio.')
        case _ if len(value) < 3:
            raise ValueError('O nome completo deve ter pelo menos 3 caracteres.')
        case _ if len(value) > 50:
            raise ValueError('O nome completo deve ter no máximo 50 caracteres.')

    # Permite letras, espaços e acentos
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', value):
        raise ValueError('O nome completo deve conter apenas letras e espaços.')

    return value


# ============================
# Username Validator
# ============================


def validate_username(value: str) -> str:
    value = value.strip()

    match value:
        case '':
            raise ValueError('O username não pode estar vazio.')
        case _ if len(value) < 3:
            raise ValueError('O username deve ter pelo menos 3 caracteres.')
        case _ if len(value) > 20:
            raise ValueError('O username deve ter no máximo 20 caracteres.')

    # Permite letras, números e underscore
    if not re.match(r'^[A-Za-z][A-Za-z0-9_]+$', value):
        raise ValueError(
            'O username deve começar com uma letra e conter apenas letras, números ou underscores.'
        )

    # Nomes reservados
    reserved = {'admin', 'root', 'superuser', 'system', 'null'}
    if value.lower() in reserved:
        raise ValueError('Este username é reservado e não pode ser utilizado.')

    return value


# ============================
# Email Validator
# ============================


def validate_email(value: EmailStr) -> EmailStr:
    """
    Valida email além do formato básico do Pydantic.
    Aqui você pode adicionar regras de negócio específicas.
    """
    email = value.lower().strip()

    # Bloquear domínios descartáveis (opcional)
    disposable_domains = {
        'mailinator.com',
        'yopmail.com',
        'tempmail.com',
        '10minutemail.com',
        'guerrillamail.com',
    }

    domain = email.split('@')[-1]
    if domain in disposable_domains:
        raise ValueError('Emails de domínio descartável não são permitidos.')

    # Tamanho máximo recomendado
    if len(email) > 120:
        raise ValueError('O email deve ter no máximo 120 caracteres.')

    return email
