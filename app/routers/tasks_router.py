

from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models import (
    TaskCreateRequest,
    TaskResponse,
    TaskListResponse,
    TaskCreatorInfo,
    SuccessResponse
)
from app.database import supabase
from app.auth import get_current_user
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


def parse_task_with_creator(task_data: dict) -> TaskResponse:
   
    # Extract creator info if available
    creator_info = None
    if "profiles" in task_data and task_data["profiles"]:
        creator_data = task_data["profiles"]
        creator_info = TaskCreatorInfo(
            id=creator_data["id"],
            full_name=creator_data.get("full_name"),
            username=creator_data.get("username"),
            email=creator_data["email"]
        )

    return TaskResponse(
        id=task_data["id"],
        title=task_data["title"],
        description=task_data["description"],
        category=task_data["category"],
        budget=Decimal(str(task_data["budget"])),
        status=task_data["status"],
        creator_id=task_data["creator_id"],
        assigned_to=task_data.get("assigned_to"),
        deadline=datetime.fromisoformat(task_data["deadline"].replace("Z", "+00:00")) if task_data.get("deadline") else None,
        tags=task_data.get("tags", []),
        created_at=datetime.fromisoformat(task_data["created_at"].replace("Z", "+00:00")),
        updated_at=datetime.fromisoformat(task_data["updated_at"].replace("Z", "+00:00")),
        creator=creator_info
    )


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="SKIL-11: Post Micro Task",
    description="Create a new micro-task (requires authentication)"
)
async def create_task(
    task_data: TaskCreateRequest,
    current_user: dict = Depends(get_current_user)
):

    try:
        # Prepare task data for insertion
        task_insert_data = {
            "title": task_data.title,
            "description": task_data.description,
            "category": task_data.category,
            "budget": float(task_data.budget),
            "creator_id": current_user.id,
            "status": "open",
            "tags": task_data.tags or []
        }

        # Add deadline if provided
        if task_data.deadline:
            task_insert_data["deadline"] = task_data.deadline.isoformat()

        # Insert task into database
        response = supabase.table("tasks").insert(task_insert_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

        # Fetch the created task with creator information
        task_id = response.data[0]["id"]
        task_response = supabase.table("tasks").select(
            "*, profiles!tasks_creator_id_fkey(*)"
        ).eq("id", task_id).execute()

        if not task_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created task"
            )

        return parse_task_with_creator(task_response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task creation failed: {str(e)}"
        )


@router.get(
    "/",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="SKIL-12: Browse Tasks",
    description="Fetch all open tasks with creator information"
)
async def browse_tasks(
    status_filter: str = Query("open", description="Filter tasks by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip")
):
   
    try:
        # Query tasks with creator information
        query = supabase.table("tasks").select(
            "*, profiles!tasks_creator_id_fkey(*)",
            count="exact"
        )

        # Apply status filter
        if status_filter:
            query = query.eq("status", status_filter)

        # Apply pagination and ordering
        response = query.order(
            "created_at", desc=True
        ).range(offset, offset + limit - 1).execute()

        # Parse tasks
        tasks = [parse_task_with_creator(task) for task in response.data]

        return TaskListResponse(
            tasks=tasks,
            total=response.count or 0
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@router.get(
    "/search",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="SKIL-13: Search Tasks",
    description="Search tasks by keyword in title or category"
)
async def search_tasks(
    keyword: Optional[str] = Query(None, min_length=1, description="Search keyword for title or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_budget: Optional[Decimal] = Query(None, ge=0, description="Minimum budget"),
    max_budget: Optional[Decimal] = Query(None, ge=0, description="Maximum budget"),
    status_filter: str = Query("open", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip")
):
   
    try:
        # Start with base query
        query = supabase.table("tasks").select(
            "*, profiles!tasks_creator_id_fkey(*)",
            count="exact"
        )

        # Apply status filter
        query = query.eq("status", status_filter)

        # Apply category filter
        if category:
            query = query.eq("category", category)

        # Apply budget filters
        if min_budget is not None:
            query = query.gte("budget", float(min_budget))
        if max_budget is not None:
            query = query.lte("budget", float(max_budget))

        # Apply keyword search (search in title)
        if keyword:
            # Use ilike for case-insensitive pattern matching
            query = query.or_(
                f"title.ilike.%{keyword}%,description.ilike.%{keyword}%"
            )

        # Execute query with ordering and pagination
        response = query.order(
            "created_at", desc=True
        ).range(offset, offset + limit - 1).execute()

        # Parse tasks
        tasks = [parse_task_with_creator(task) for task in response.data]

        return TaskListResponse(
            tasks=tasks,
            total=response.count or 0
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Task Details",
    description="Fetch detailed information about a specific task"
)
async def get_task(task_id: str):
    
    try:
        response = supabase.table("tasks").select(
            "*, profiles!tasks_creator_id_fkey(*)"
        ).eq("id", task_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return parse_task_with_creator(response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task: {str(e)}"
        )
