from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.auth import get_current_user
from app.database import supabase
from typing import Optional

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user=Depends(get_current_user)):
    """Check if current user has admin role."""
    user_meta = getattr(current_user, "user_metadata", {}) or {}
    app_meta = getattr(current_user, "app_metadata", {}) or {}
    role = app_meta.get("role") or user_meta.get("role", "")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required."
        )
    return current_user


@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user=Depends(require_admin)
):
    """Admin: get paginated list of all users."""
    offset = (page - 1) * limit

    query = supabase.table("profiles").select("*", count="exact")

    if search:
        query = query.or_(f"full_name.ilike.%{search}%,email.ilike.%{search}%,username.ilike.%{search}%")

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

    return {
        "users": result.data or [],
        "total": result.count or 0,
        "page": page,
        "limit": limit,
    }


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user=Depends(require_admin)):
    """Admin: delete a user profile."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account.")

    result = supabase.table("profiles").delete().eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found.")

    return {"message": "User deleted successfully.", "user_id": user_id}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user=Depends(require_admin)):
    """Admin: delete any task."""
    result = supabase.table("tasks").delete().eq("id", task_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found.")

    return {"message": "Task deleted successfully.", "task_id": task_id}


@router.delete("/ratings/{rating_id}")
async def delete_rating(rating_id: str, current_user=Depends(require_admin)):
    """Admin: delete a rating/review."""
    result = supabase.table("ratings").delete().eq("id", rating_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Rating not found.")

    return {"message": "Rating deleted successfully.", "rating_id": rating_id}


@router.get("/stats")
async def get_platform_stats(current_user=Depends(require_admin)):
    """Admin: get overall platform statistics."""
    users = supabase.table("profiles").select("id", count="exact").execute()
    tasks = supabase.table("tasks").select("id", count="exact").execute()
    open_tasks = supabase.table("tasks").select("id", count="exact").eq("status", "open").execute()
    completed = supabase.table("tasks").select("id", count="exact").eq("status", "completed").execute()
    ratings = supabase.table("ratings").select("id", count="exact").execute()

    return {
        "total_users": users.count or 0,
        "total_tasks": tasks.count or 0,
        "open_tasks": open_tasks.count or 0,
        "completed_tasks": completed.count or 0,
        "total_ratings": ratings.count or 0,
    }