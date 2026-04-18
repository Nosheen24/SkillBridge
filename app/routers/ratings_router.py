from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user
from app.database import supabase
from app.models import RatingCreateRequest, RatingResponse, RatingsListResponse
from typing import Optional

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("/{rated_user_id}", response_model=RatingResponse)
async def give_rating(
    rated_user_id: str,
    payload: RatingCreateRequest,
    current_user=Depends(get_current_user)
):
    """Give a rating and review to a freelancer for a completed task."""
    rater_id = current_user.id

    if rater_id == rated_user_id:
        raise HTTPException(status_code=400, detail="You cannot rate yourself.")

    # Verify task exists and is completed
    task_res = supabase.table("tasks").select("*").eq("id", payload.task_id).single().execute()
    if not task_res.data:
        raise HTTPException(status_code=404, detail="Task not found.")
    task = task_res.data

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="You can only rate on completed tasks.")

    # Verify rater was involved (creator or assigned)
    if rater_id != task["creator_id"] and rater_id != task.get("assigned_to"):
        raise HTTPException(status_code=403, detail="You were not part of this task.")

    # Check duplicate
    existing = (
        supabase.table("ratings")
        .select("id")
        .eq("task_id", payload.task_id)
        .eq("rated_user_id", rated_user_id)
        .eq("rater_user_id", rater_id)
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=400, detail="You have already rated this user for this task.")

    insert_data = {
        "task_id": payload.task_id,
        "rated_user_id": rated_user_id,
        "rater_user_id": rater_id,
        "rating": payload.rating,
        "review": payload.review,
    }

    result = supabase.table("ratings").insert(insert_data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to submit rating.")

    return result.data[0]


@router.get("/user/{user_id}", response_model=RatingsListResponse)
async def get_user_ratings(user_id: str):
    """Get all ratings and reviews for a specific user."""
    # Use simple select to avoid foreign key alias issues
    result = (
        supabase.table("ratings")
        .select("*, task:tasks(title)")
        .eq("rated_user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    
    # Fetch rater profile separately for each rating
    ratings_data = result.data or []
    for r in ratings_data:
        try:
            rater = supabase.table("profiles").select("full_name, username").eq("id", r["rater_user_id"]).single().execute()
            r["rater"] = rater.data if rater.data else {}
        except:
            r["rater"] = {}

    ratings = ratings_data
    total = len(ratings)
    avg = round(sum(r["rating"] for r in ratings) / total, 1) if total else 0.0

    return {
        "ratings": ratings,
        "total": total,
        "average_rating": avg,
    }