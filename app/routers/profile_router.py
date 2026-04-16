from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime

from fastapi import UploadFile, File      # Skil-20 changes
from supabase import create_client
from app.config import get_settings
import uuid
import mimetypes

from app.models import (
    SkillProfileCreateRequest,
    SkillProfileUpdateRequest,
    SkillProfileResponse,
    PortfolioLinkRequest,
)

from app.database import supabase
from app.auth import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

settings = get_settings()                   # Skil-20 changes
service_client = create_client(
    settings.supabase_url,
    settings.supabase_service_key
)

ALLOWED_FILE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_MIME_PREFIXES = ("image/",)
PORTFOLIO_BUCKET = "portfolios"
AVATAR_BUCKET = "avatars"

def parse_profile(profile_data: dict) -> SkillProfileResponse:
    return SkillProfileResponse(
        id=profile_data["id"],
        email=profile_data["email"],
        full_name=profile_data.get("full_name"),
        username=profile_data.get("username"),
        bio=profile_data.get("bio"),
        skills=profile_data.get("skills", []),
        experience=profile_data.get("experience"),
        student_id=profile_data.get("student_id"),
        university=profile_data.get("university"),
        avatar_url=profile_data.get("avatar_url"),
        portfolio_url=profile_data.get("portfolio_url"),
        portfolio_filename=profile_data.get("portfolio_filename"),
        portfolio_type=profile_data.get("portfolio_type"),
        portfolio_link=profile_data.get("portfolio_link"),
        created_at=datetime.fromisoformat(profile_data["created_at"].replace("Z", "+00:00")),
        updated_at=datetime.fromisoformat(profile_data["updated_at"].replace("Z", "+00:00"))
    )


# 🔹 GET PROFILE
@router.get(
    "/me",
    response_model=SkillProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile"
)
async def get_my_profile(current_user = Depends(get_current_user)):
    try:
        response = service_client.table("profiles") \
            .select("*") \
            .eq("id", current_user.id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        return parse_profile(response.data[0])

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch profile: {str(e)}"
        )


# 🔹 CREATE / UPDATE SKILL PROFILE
@router.post(
    "/me",
    response_model=SkillProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="SKIL-18: Create Skill Profile",
    description="Save skills, experience, and description for the current user"
)
async def create_skill_profile(
    profile_data: SkillProfileCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check profile exists
        existing_profile = service_client.table("profiles") \
            .select("*") \
            .eq("id", current_user.id) \
            .execute()

        if not existing_profile.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Update profile
        updated = service_client.table("profiles").update({
            "skills": profile_data.skills,
            "experience": profile_data.experience,
            "bio": profile_data.bio
        }).eq("id", current_user.id).execute()

        if not updated.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to save skill profile"
            )

        return parse_profile(updated.data[0])

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to save skill profile: {str(e)}"
        )
# new file made in sprint 3 skil-18

# Skil-19 changes
@router.put(
    "/me",
    response_model=SkillProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="SKIL-19: Edit Profile",
    description="Update skills, experience, and bio for current user"
)
async def edit_skill_profile(
    profile_data: SkillProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check profile exists
        existing_profile = service_client.table("profiles") \
            .select("*") \
            .eq("id", current_user.id) \
            .execute()

        if not existing_profile.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Update profile
        updated = service_client.table("profiles").update({
            "skills": profile_data.skills,
            "experience": profile_data.experience,
            "bio": profile_data.bio
        }).eq("id", current_user.id).execute()

        if not updated.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to update profile"
            )

        return parse_profile(updated.data[0])

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update profile: {str(e)}"
        )
        
# Skil-20 changes
@router.post(
    "/me/avatar",
    response_model=SkillProfileResponse,
    summary="Upload profile picture"
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")

        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or ""
        if not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")

        file_bytes = await file.read()
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
        unique_filename = f"{current_user.id}/avatar.{ext}"

        # Delete old avatar if exists, then upload new one
        try:
            service_client.storage.from_(AVATAR_BUCKET).remove([unique_filename])
        except Exception:
            pass

        service_client.storage.from_(AVATAR_BUCKET).upload(
            unique_filename,
            file_bytes,
            {"content-type": content_type, "upsert": "true"}
        )

        public_url = service_client.storage.from_(AVATAR_BUCKET).get_public_url(unique_filename)

        updated = service_client.table("profiles").update({
            "avatar_url": public_url
        }).eq("id", current_user.id).execute()

        return parse_profile(updated.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/me/portfolio/upload",
    response_model=SkillProfileResponse,
    summary="SKIL-20: Upload Portfolio File"
)
async def upload_portfolio_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")

        filename_lower = file.filename.lower()
        extension = "." + filename_lower.rsplit(".", 1)[-1] if "." in filename_lower else ""

        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or ""

        if extension not in ALLOWED_FILE_EXTENSIONS and not content_type.startswith(ALLOWED_MIME_PREFIXES):
            raise HTTPException(status_code=400, detail="Invalid file type")

        file_bytes = await file.read()

        unique_filename = f"{current_user.id}/{uuid.uuid4()}_{file.filename}"

        service_client.storage.from_(PORTFOLIO_BUCKET).upload(
            unique_filename,
            file_bytes,
            {"content-type": content_type}
        )

        public_url = service_client.storage.from_(PORTFOLIO_BUCKET).get_public_url(unique_filename)

        portfolio_type = "image" if content_type.startswith("image/") else "pdf"

        updated = service_client.table("profiles").update({
            "portfolio_url": public_url,
            "portfolio_filename": file.filename,
            "portfolio_type": portfolio_type,
            "portfolio_link": None
        }).eq("id", current_user.id).execute()

        return parse_profile(updated.data[0])

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post(
    "/me/portfolio/link",
    response_model=SkillProfileResponse,
    summary="SKIL-20: Save Portfolio Link"
)
async def save_portfolio_link(
    portfolio_data: PortfolioLinkRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        updated = service_client.table("profiles").update({
            "portfolio_url": None,
            "portfolio_filename": None,
            "portfolio_type": "link",
            "portfolio_link": portfolio_data.portfolio_link
        }).eq("id", current_user.id).execute()

        return parse_profile(updated.data[0])

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))