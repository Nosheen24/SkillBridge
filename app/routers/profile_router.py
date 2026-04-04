from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime

from app.models import SkillProfileCreateRequest, SkillProfileResponse
from app.database import supabase
from app.auth import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


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
        response = supabase.table("profiles") \
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
        existing_profile = supabase.table("profiles") \
            .select("*") \
            .eq("id", current_user.id) \
            .execute()

        if not existing_profile.data:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Update profile
        updated = supabase.table("profiles").update({
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