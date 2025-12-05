"""
User service for authentication operations.
Handles user registration, login, email verification, and password reset.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
import weaviate

from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    generate_verification_code,
)
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token
from app.db.weaviate_client import get_weaviate_client


class UserService:
    """Service class for user authentication and management."""
    
    def __init__(self):
        """Initialize UserService."""
        self.collection_name = "Users"
    
    def _get_collection(self):
        """Get Users collection from Weaviate."""
        client = get_weaviate_client()
        if client is None:
            raise Exception("Weaviate client not connected")
        return client.collections.get(self.collection_name)
    
    def _find_user_by_email(self, email: str) -> Optional[dict]:
        """Find user by email address."""
        try:
            collection = self._get_collection()
            
            # Query for user with matching email
            response = collection.query.fetch_objects(
                filters=weaviate.classes.query.Filter.by_property("email").equal(email),
                limit=1
            )
            
            if response.objects and len(response.objects) > 0:
                user_obj = response.objects[0]
                return {
                    "uuid": str(user_obj.uuid),
                    **user_obj.properties
                }
            
            return None
            
        except Exception as e:
            print(f"Error finding user by email: {str(e)}")
            return None
    
    def register_user(self, user_data: UserCreate) -> Tuple[bool, str, Optional[dict]]:
        """
        Register a new user.
        
        Returns:
            (success, message, user_data)
        """
        try:
            # Validate password strength
            is_valid, error_msg = validate_password_strength(user_data.password)
            if not is_valid:
                return False, error_msg, None
            
            # Check if user already exists
            existing_user = self._find_user_by_email(user_data.email)
            if existing_user:
                return False, "User with this email already exists", None
            
            # Generate verification code
            verification_code = generate_verification_code()
            verification_expires = (datetime.utcnow() + timedelta(hours=24)).isoformat()
            
            # Hash password
            password_hash = hash_password(user_data.password)
            
            # Create user ID
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            
            # Prepare user data
            user_properties = {
                "user_id": user_id,
                "email": user_data.email,
                "password_hash": password_hash,
                "is_verified": False,
                "verification_code": verification_code,
                "verification_code_expires": verification_expires,
                "reset_code": "",
                "reset_code_expires": "",
                "created_at": datetime.utcnow().isoformat(),
                "last_login": "",
            }
            
            # Insert into Weaviate
            collection = self._get_collection()
            collection.data.insert(properties=user_properties)
            
            # Log verification code (instead of sending email)
            print("\n" + "="*60)
            print("📧 EMAIL VERIFICATION CODE (Check Terminal)")
            print("="*60)
            print(f"Email: {user_data.email}")
            print(f"Verification Code: {verification_code}")
            print(f"Expires: {verification_expires}")
            print("="*60 + "\n")
            
            return True, "Registration successful. Please check your email (terminal logs) for verification code.", {
                "user_id": user_id,
                "email": user_data.email,
                "is_verified": False,
                "created_at": user_properties["created_at"]
            }
            
        except Exception as e:
            print(f"Error registering user: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
    
    def verify_email(self, email: str, verification_code: str) -> Tuple[bool, str]:
        """
        Verify user email with verification code.
        
        Returns:
            (success, message)
        """
        try:
            user = self._find_user_by_email(email)
            if not user:
                return False, "User not found"
            
            if user["is_verified"]:
                return False, "Email already verified"
            
            # Check verification code
            if user["verification_code"] != verification_code:
                return False, "Invalid verification code"
            
            # Check if code expired
            expires_at = datetime.fromisoformat(user["verification_code_expires"])
            if datetime.utcnow() > expires_at:
                return False, "Verification code expired. Please request a new one."
            
            # Update user as verified
            collection = self._get_collection()
            collection.data.update(
                uuid=user["uuid"],
                properties={
                    "is_verified": True,
                    "verification_code": "",  # Clear code after verification
                }
            )
            
            return True, "Email verified successfully. You can now login."
            
        except Exception as e:
            print(f"Error verifying email: {str(e)}")
            return False, f"Verification failed: {str(e)}"
    
    def login_user(self, login_data: UserLogin) -> Tuple[bool, str, Optional[Token]]:
        """
        Authenticate user and return JWT token.
        
        Returns:
            (success, message, token_data)
        """
        try:
            # Find user
            user = self._find_user_by_email(login_data.email)
            if not user:
                return False, "Invalid email or password", None
            
            # Verify password
            if not verify_password(login_data.password, user["password_hash"]):
                return False, "Invalid email or password", None
            
            # Check if email is verified
            if not user["is_verified"]:
                return False, "Please verify your email before logging in", None
            
            # Update last login
            collection = self._get_collection()
            collection.data.update(
                uuid=user["uuid"],
                properties={"last_login": datetime.utcnow().isoformat()}
            )
            
            # Create JWT token
            access_token = create_access_token(
                data={"sub": user["email"], "user_id": user["user_id"]}
            )
            
            # Prepare response
            user_response = UserResponse(
                user_id=user["user_id"],
                email=user["email"],
                is_verified=user["is_verified"],
                created_at=user["created_at"]
            )
            
            token_response = Token(
                access_token=access_token,
                token_type="bearer",
                user=user_response
            )
            
            return True, "Login successful", token_response
            
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False, f"Login failed: {str(e)}", None
    
    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """
        Generate password reset code and send to user.
        
        Returns:
            (success, message)
        """
        try:
            user = self._find_user_by_email(email)
            if not user:
                # Don't reveal if user exists for security
                return True, "If the email exists, a password reset code has been sent."
            
            # Generate reset code
            reset_code = generate_verification_code()
            reset_expires = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            
            # Update user with reset code
            collection = self._get_collection()
            collection.data.update(
                uuid=user["uuid"],
                properties={
                    "reset_code": reset_code,
                    "reset_code_expires": reset_expires,
                }
            )
            
            # Log reset code (instead of sending email)
            print("\n" + "="*60)
            print("🔑 PASSWORD RESET CODE (Check Terminal)")
            print("="*60)
            print(f"Email: {email}")
            print(f"Reset Code: {reset_code}")
            print(f"Expires: {reset_expires}")
            print("="*60 + "\n")
            
            return True, "Password reset code sent. Please check your email (terminal logs)."
            
        except Exception as e:
            print(f"Error requesting password reset: {str(e)}")
            return False, f"Password reset request failed: {str(e)}"
    
    def reset_password(self, email: str, reset_code: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset user password with reset code.
        
        Returns:
            (success, message)
        """
        try:
            # Validate new password strength
            is_valid, error_msg = validate_password_strength(new_password)
            if not is_valid:
                return False, error_msg
            
            user = self._find_user_by_email(email)
            if not user:
                return False, "Invalid reset code"
            
            # Check reset code
            if user["reset_code"] != reset_code or not user["reset_code"]:
                return False, "Invalid reset code"
            
            # Check if code expired
            expires_at = datetime.fromisoformat(user["reset_code_expires"])
            if datetime.utcnow() > expires_at:
                return False, "Reset code expired. Please request a new one."
            
            # Hash new password
            password_hash = hash_password(new_password)
            
            # Update password and clear reset code
            collection = self._get_collection()
            collection.data.update(
                uuid=user["uuid"],
                properties={
                    "password_hash": password_hash,
                    "reset_code": "",
                    "reset_code_expires": "",
                }
            )
            
            return True, "Password reset successfully. You can now login with your new password."
            
        except Exception as e:
            print(f"Error resetting password: {str(e)}")
            return False, f"Password reset failed: {str(e)}"


# Global service instance
user_service = UserService()
