"""
Security utilities for authentication and authorization.
Handles password hashing, JWT token management, and verification codes.
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
import string

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ===================== PASSWORD HASHING =====================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# ===================== PASSWORD VALIDATION =====================
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements:
    - At least 8 characters
    - Contains at least one number
    - Contains at least one special character
    
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    special_chars = set(string.punctuation)
    if not any(char in special_chars for char in password):
        return False, "Password must contain at least one special character (!@#$%^&*)"
    
    return True, ""


# ===================== JWT TOKEN MANAGEMENT =====================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing user data to encode (e.g., {"sub": "user@example.com"})
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # Default 24 hours
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ===================== VERIFICATION CODE GENERATION =====================
def generate_verification_code(length: int = 6) -> str:
    """
    Generate a random verification code for email verification or password reset.
    
    Args:
        length: Length of the verification code (default 6)
    
    Returns:
        Random alphanumeric code (e.g., "A3X9K2")
    """
    characters = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(characters) for _ in range(length))
    return code


def generate_reset_token() -> str:
    """
    Generate a secure random token for password reset links.
    
    Returns:
        32-character hex token
    """
    return secrets.token_hex(32)
