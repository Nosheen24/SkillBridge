from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models import (        # Sprint 3 changes(Skil-17)
    TaskCreateRequest,
    TaskResponse,
    TaskListResponse,
    TaskCreatorInfo,
    SuccessResponse,
    ApplicantDecisionRequest,
    ApplicantDecisionResponse
)
from app.database import supabase
from app.auth import get_current_user
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.config import get_settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client

_security = HTTPBearer()

def _authed_client(token: str):
    """Create a Supabase client with the user's JWT so RLS read policies are satisfied."""
    s = get_settings()
    client = create_client(s.supabase_url, s.supabase_key)
    client.postgrest.auth(token)
    return client

def _service_client():
    """Create a Supabase client with the service_role key to bypass RLS for writes."""
    s = get_settings()
    if not s.supabase_service_key or s.supabase_service_key == "your_service_role_key_here":
        raise HTTPException(
            status_code=500,
            detail="SUPABASE_SERVICE_KEY is not configured. Add your service_role key to .env."
        )
    client = create_client(s.supabase_url, s.supabase_service_key)
    return client

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


@router.post(
    "/{task_id}/apply",
    status_code=status.HTTP_201_CREATED,
    summary="SKIL-15: Apply/Bid on Task",
    description="Apply to work on a task (requires authentication)"
)
async def apply_for_task(
    task_id: str,
    message: str = "",
    current_user: dict = Depends(get_current_user)
):
    try:
        task = supabase.table("tasks").select("*").eq("id", task_id).execute()
        if not task.data:
            raise HTTPException(status_code=404, detail="Task not found")

        existing = supabase.table("task_applications").select("*").eq(
            "task_id", task_id).eq("applicant_id", current_user.id).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Already applied for this task")

        application = supabase.table("task_applications").insert({
            "task_id": task_id,
            "applicant_id": current_user.id,
            "message": message,
            "status": "pending"
        }).execute()

        return {"message": "Application submitted successfully", "data": application.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Application failed: {str(e)}")

@router.get(
    "/{task_id}/applicants",
    status_code=status.HTTP_200_OK,
    summary="SKIL-16: View Applicants",
    description="View all applicants for a task (only task creator can view)"
)
async def view_applicants(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    current_user: dict = Depends(get_current_user)
):
    try:
        db = _authed_client(credentials.credentials)

        # Check task exists and user is the creator
        task = db.table("tasks").select("*").eq("id", task_id).execute()
        if not task.data:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.data[0]["creator_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Only task creator can view applicants")

        # Get all applications for this task
        applications = db.table("task_applications").select(
            "*, profiles!task_applications_applicant_id_fkey(*)"
        ).eq("task_id", task_id).execute()

        return {
            "task_id": task_id,
            "total_applicants": len(applications.data),
            "applicants": applications.data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch applicants: {str(e)}")

# Sprint 3 Skil-17 changes

@router.patch(
    "/{task_id}/applications/{application_id}",
    response_model=ApplicantDecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="SKIL-17: Accept/Reject Applicant",
    description="Accept or reject an applicant for a task (only task creator can do this)"
)
async def decide_applicant(
    task_id: str,
    application_id: str,
    decision_data: ApplicantDecisionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    current_user: dict = Depends(get_current_user)
):
    try:
        read_db = _authed_client(credentials.credentials)
        write_db = _service_client()

        # 1. Check task exists
        task_response = read_db.table("tasks").select("*").eq("id", task_id).execute()

        if not task_response.data:
            raise HTTPException(status_code=404, detail="Task not found")

        task = task_response.data[0]

        # 2. Only creator allowed
        if task["creator_id"] != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only task creator can accept or reject applicants"
            )

        # 3. Check application exists
        application_response = read_db.table("task_applications").select("*")\
            .eq("id", application_id)\
            .eq("task_id", task_id)\
            .execute()

        if not application_response.data:
            raise HTTPException(status_code=404, detail="Application not found")

        application = application_response.data[0]

        # 4. Prevent duplicate decision
        if application["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Application already {application['status']}"
            )

        # 5. Update selected application (service_role bypasses RLS for cross-user write)
        updated_application = write_db.table("task_applications").update(
            {"status": decision_data.decision}
        ).eq("id", application_id).execute()

        if not updated_application.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to update application status"
            )

        # 6. If accepted → assign task + reject others
        if decision_data.decision == "accepted":

            # Assign task
            task_update = write_db.table("tasks").update({
                "assigned_to": application["applicant_id"],
                "status": "in_progress"
            }).eq("id", task_id).execute()

            if not task_update.data:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update task"
                )

            # Reject all others
            write_db.table("task_applications").update(
                {"status": "rejected"}
            ).eq("task_id", task_id)\
             .eq("status", "pending")\
             .neq("id", application_id)\
             .execute()

        return ApplicantDecisionResponse(
            message=f"Applicant {decision_data.decision} successfully",
            application_id=updated_application.data[0]["id"],
            task_id=updated_application.data[0]["task_id"],
            applicant_id=updated_application.data[0]["applicant_id"],
            status=updated_application.data[0]["status"]
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process decision: {str(e)}"
        )

@router.patch(
    "/{task_id}/complete",
    status_code=status.HTTP_200_OK,
    summary="SKIL-14: Mark Task Complete",
    description="Mark a task as complete (only task creator can do this)"
)
async def mark_task_complete(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check task exists and user is the creator
        task = supabase.table("tasks").select("*").eq("id", task_id).execute()
        if not task.data:
            raise HTTPException(status_code=404, detail="Task not found")

        # if task.data[0]["creator_id"] != current_user["id"]:
        if task.data[0]["creator_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Only task creator can mark task as complete")

        if task.data[0]["status"] == "completed":
            raise HTTPException(status_code=400, detail="Task is already completed")

        # Update task status to completed (use service client to bypass RLS)
        write_db = _service_client()
        updated = write_db.table("tasks").update(
            {"status": "completed"}
        ).eq("id", task_id).execute()

        if not updated.data:
            raise HTTPException(status_code=500, detail="Failed to update task status")

        return {"message": "Task marked as complete", "task_id": task_id, "status": "completed"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to mark task complete: {str(e)}")