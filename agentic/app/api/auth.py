"""
Authentication API endpoints.
Handles user registration, login, email verification, and password reset.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    UserCreate,
    UserLogin,
    Token,
    EmailVerification,
    PasswordResetRequest,
    PasswordReset,
)
from app.services.user_service import user_service


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters, must include number and special character
    
    Returns registration success and verification instructions.
    Verification code will be displayed in terminal logs.
    """
    success, message, user = user_service.register_user(user_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "user": user,
        "note": "Check terminal logs for verification code"
    }


@router.post("/verify-email")
async def verify_email(verification: EmailVerification):
    """
    Verify user email with verification code.
    
    - **email**: User email address
    - **verification_code**: 6-character code from terminal logs
    
    Email must be verified before login is allowed.
    """
    success, message = user_service.verify_email(
        verification.email,
        verification.verification_code
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Authenticate user and return JWT access token.
    
    - **email**: User email address
    - **password**: User password
    
    Returns JWT token for authenticated requests.
    Token is valid for 24 hours.
    """
    success, message, token = user_service.login_user(login_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """
    Request password reset code.
    
    - **email**: User email address
    
    Generates a password reset code valid for 1 hour.
    Code will be displayed in terminal logs.
    """
    success, message = user_service.request_password_reset(request.email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "note": "Check terminal logs for reset code"
    }


@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """
    Reset password using reset code.
    
    - **email**: User email address
    - **reset_code**: 6-character code from terminal logs
    - **new_password**: New password (min 8 chars, must include number and special char)
    
    Password will be updated and user can login with new password.
    """
    success, message = user_service.reset_password(
        reset_data.email,
        reset_data.reset_code,
        reset_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }
