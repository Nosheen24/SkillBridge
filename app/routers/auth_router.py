

from fastapi import APIRouter, HTTPException, status
from app.models import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserProfile,
    ErrorResponse
)
from app.database import supabase
from datetime import datetime

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="SKIL-7: User Registration",
    description="Register a new user account using Supabase Auth"
)
async def register_user(user_data: UserRegisterRequest):
  
    try:
        # Sign up user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name,
                    "username": user_data.username,
                    "bio": user_data.bio,
                    "skills": user_data.skills,
                    "student_id": user_data.student_id,
                    "university": user_data.university
                }
            }
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Email may already be in use."
            )

        # Fetch the created profile from database
        profile_response = supabase.table("profiles").select("*").eq(
            "id", auth_response.user.id
        ).execute()

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Profile creation failed"
            )

        profile_data = profile_response.data[0]

        # Convert to UserProfile model
        user_profile = UserProfile(
            id=profile_data["id"],
            email=profile_data["email"],
            full_name=profile_data.get("full_name"),
            username=profile_data.get("username"),
            bio=profile_data.get("bio"),
            skills=profile_data.get("skills", []),
            student_id=profile_data.get("student_id"),
            university=profile_data.get("university"),
            created_at=datetime.fromisoformat(profile_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(profile_data["updated_at"].replace("Z", "+00:00"))
        )

        return UserRegisterResponse(
            message="User registered successfully",
            user_id=auth_response.user.id,
            user=user_profile
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="SKIL-8: User Login",
    description="Authenticate user and return JWT access token"
)
async def login_user(credentials: UserLoginRequest):
    
    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Fetch user profile
        profile_response = supabase.table("profiles").select("*").eq(
            "id", auth_response.user.id
        ).execute()

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        profile_data = profile_response.data[0]

        # Convert to UserProfile model
        user_profile = UserProfile(
            id=profile_data["id"],
            email=profile_data["email"],
            full_name=profile_data.get("full_name"),
            username=profile_data.get("username"),
            bio=profile_data.get("bio"),
            skills=profile_data.get("skills", []),
            student_id=profile_data.get("student_id"),
            university=profile_data.get("university"),
            created_at=datetime.fromisoformat(profile_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(profile_data["updated_at"].replace("Z", "+00:00"))
        )

        return UserLoginResponse(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            user=user_profile,
            expires_in=auth_response.session.expires_in or 3600
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )
