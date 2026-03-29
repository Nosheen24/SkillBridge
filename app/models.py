from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ===== AUTH MODELS =====

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = []
    student_id: Optional[str] = None
    university: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = []
    student_id: Optional[str] = None
    university: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserRegisterResponse(BaseModel):
    message: str
    user_id: str
    user: UserProfile

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile
    expires_in: int

class PasswordResetRequest(BaseModel):
    email: EmailStr

class SetNewPasswordRequest(BaseModel):
    new_password: str

class ErrorResponse(BaseModel):
    detail: str


# ===== TASK MODELS =====

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    skills_required: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    budget: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    location: Optional[str] = None

class TaskCreatorInfo(BaseModel):
    id: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    university: Optional[str] = None
    email: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    skills_required: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    budget: Optional[float] = None
    status: Optional[str] = None
    creator_id: Optional[str] = None
    assigned_to: Optional[str] = None
    deadline: Optional[datetime] = None
    location: Optional[str] = None
    creator: Optional[TaskCreatorInfo] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int

class SuccessResponse(BaseModel):
    message: str