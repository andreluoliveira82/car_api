# car_api/core/security.py
# ==============================================================================
# File: car_api/core/security.py
# Description: This module provides security-related utilities for the Car API, including password hashing and verification.
# ==============================================================================

from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """
    Hashes a password using the recommended hashing algorithm.
    Args:
        password (str): The plain text password to hash.
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.
    Returns:
        bool: True if the password is correct, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
