"""
User service for authentication operations.
Handles user registration, login, email verification, and password reset.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    generate_verification_code,
)
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token
from app.db.models import User
from app.db.postgres_client import postgres_manager


class UserService:
    """Service class for user authentication and management."""
    
    def __init__(self):
        """Initialize UserService."""
        pass
    
    def _get_db(self) -> Session:
        """Get database session from SessionLocal."""
        if postgres_manager.SessionLocal is None:
            raise Exception("Database not connected")
        return postgres_manager.SessionLocal()
    
    def _find_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Find user by email address."""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            print(f"Error finding user by email: {str(e)}")
            return None
    
    def register_user(self, user_data: UserCreate) -> Tuple[bool, str, Optional[dict]]:
        """
        Register a new user.
        
        Returns:
            (success, message, user_data)
        """
        db = None
        try:
            # Validate password strength
            is_valid, error_msg = validate_password_strength(user_data.password)
            if not is_valid:
                return False, error_msg, None
            
            db = self._get_db()
            
            # Check if user already exists
            existing_user = self._find_user_by_email(db, user_data.email)
            if existing_user:
                return False, "User with this email already exists", None
            
            # Generate verification code
            verification_code = generate_verification_code()
            verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
            
            # Hash password
            password_hash = hash_password(user_data.password)
            
            # Create user ID
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            
            # Create user object
            new_user = User(
                user_id=user_id,
                email=user_data.email,
                password_hash=password_hash,
                is_verified=False,
                verification_code=verification_code,
                verification_code_expires=verification_expires,
            )
            
            # Insert into database
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Log verification code (instead of sending email)
            print("\n" + "="*60)
            print("📧 EMAIL VERIFICATION CODE (Check Terminal)")
            print("="*60)
            print(f"Email: {user_data.email}")
            print(f"Verification Code: {verification_code}")
            print(f"Expires: {verification_expires.isoformat()}")
            print("="*60 + "\n")
            
            return True, "Registration successful. Please check your email (terminal logs) for verification code.", {
                "user_id": new_user.user_id,
                "email": new_user.email,
                "is_verified": new_user.is_verified,
                "created_at": new_user.created_at.isoformat()
            }
            
        except IntegrityError:
            if db:
                db.rollback()
            return False, "User with this email already exists", None
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error registering user: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
        finally:
            if db:
                db.close()
    
    def verify_email(self, email: str, verification_code: str) -> Tuple[bool, str]:
        """
        Verify user email with verification code.
        
        Returns:
            (success, message)
        """
        db = None
        try:
            db = self._get_db()
            
            user = self._find_user_by_email(db, email)
            if not user:
                return False, "User not found"
            
            if user.is_verified:
                return False, "Email already verified"
            
            # Check verification code
            if user.verification_code != verification_code:
                return False, "Invalid verification code"
            
            # Check if code expired (handle both timezone-aware and naive datetimes)
            current_time = datetime.now(timezone.utc)
            expires_time = user.verification_code_expires
            # Make comparison timezone-aware
            if expires_time.tzinfo is None:
                expires_time = expires_time.replace(tzinfo=timezone.utc)
            if current_time > expires_time:
                return False, "Verification code expired. Please request a new one."
            
            # Update user as verified
            user.is_verified = True
            user.verification_code = None
            user.verification_code_expires = None
            
            db.commit()
            
            return True, "Email verified successfully. You can now login."
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error verifying email: {str(e)}")
            return False, f"Verification failed: {str(e)}"
        finally:
            if db:
                db.close()
    
    def login_user(self, login_data: UserLogin) -> Tuple[bool, str, Optional[Token]]:
        """
        Authenticate user and return JWT token.
        
        Returns:
            (success, message, token_data)
        """
        db = None
        try:
            db = self._get_db()
            
            # Find user
            user = self._find_user_by_email(db, login_data.email)
            if not user:
                return False, "Invalid email or password", None
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                return False, "Invalid email or password", None
            
            # Check if email is verified
            if not user.is_verified:
                return False, "Please verify your email before logging in", None
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            db.commit()
            
            # Create JWT token
            access_token = create_access_token(
                data={"sub": user.email, "user_id": user.user_id}
            )
            
            # Prepare response
            user_response = UserResponse(
                user_id=user.user_id,
                email=user.email,
                is_verified=user.is_verified,
                created_at=user.created_at.isoformat()
            )
            
            token_response = Token(
                access_token=access_token,
                token_type="bearer",
                user=user_response
            )
            
            return True, "Login successful", token_response
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error during login: {str(e)}")
            return False, f"Login failed: {str(e)}", None
        finally:
            if db:
                db.close()
    
    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """
        Generate password reset code and send to user.
        
        Returns:
            (success, message)
        """
        db = None
        try:
            db = self._get_db()
            
            user = self._find_user_by_email(db, email)
            if not user:
                # Don't reveal if user exists for security
                return True, "If the email exists, a password reset code has been sent."
            
            # Generate reset code
            reset_code = generate_verification_code()
            reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
            
            # Update user with reset code
            user.reset_code = reset_code
            user.reset_code_expires = reset_expires
            db.commit()
            
            # Log reset code (instead of sending email)
            print("\n" + "="*60)
            print("🔑 PASSWORD RESET CODE (Check Terminal)")
            print("="*60)
            print(f"Email: {email}")
            print(f"Reset Code: {reset_code}")
            print(f"Expires: {reset_expires.isoformat()}")
            print("="*60 + "\n")
            
            return True, "Password reset code sent. Please check your email (terminal logs)."
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error requesting password reset: {str(e)}")
            return False, f"Password reset request failed: {str(e)}"
        finally:
            if db:
                db.close()
    
    def reset_password(self, email: str, reset_code: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset user password with reset code.
        
        Returns:
            (success, message)
        """
        db = None
        try:
            # Validate new password strength
            is_valid, error_msg = validate_password_strength(new_password)
            if not is_valid:
                return False, error_msg
            
            db = self._get_db()
            
            user = self._find_user_by_email(db, email)
            if not user:
                return False, "Invalid reset code"
            
            # Check reset code
            if not user.reset_code or user.reset_code != reset_code:
                return False, "Invalid reset code"
            
            # Check if code expired (handle both timezone-aware and naive datetimes)
            current_time = datetime.now(timezone.utc)
            expires_time = user.reset_code_expires
            # Make comparison timezone-aware
            if expires_time.tzinfo is None:
                expires_time = expires_time.replace(tzinfo=timezone.utc)
            if current_time > expires_time:
                return False, "Reset code expired. Please request a new one."
            
            # Hash new password
            password_hash = hash_password(new_password)
            
            # Update password and clear reset code
            user.password_hash = password_hash
            user.reset_code = None
            user.reset_code_expires = None
            db.commit()
            
            return True, "Password reset successfully. You can now login with your new password."
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error resetting password: {str(e)}")
            return False, f"Password reset failed: {str(e)}"
        finally:
            if db:
                db.close()


# Global service instance
user_service = UserService()
