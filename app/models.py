

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class UserRegisterRequest(BaseModel):

    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    bio: Optional[str] = Field(None, max_length=500)
    skills: Optional[List[str]] = Field(default_factory=list)
    student_id: Optional[str] = None
    university: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"
    user: "UserProfile"
    expires_in: int


class UserProfile(BaseModel):

    id: str
    email: str
    full_name: Optional[str]
    username: Optional[str]
    bio: Optional[str]
    skills: Optional[List[str]]
    student_id: Optional[str]
    university: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRegisterResponse(BaseModel):
 
    message: str
    user_id: str
    user: UserProfile

class TaskCreateRequest(BaseModel):

    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    category: str = Field(..., min_length=1, max_length=50)
    budget: Decimal = Field(..., gt=0, description="Budget must be greater than 0")
    deadline: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)

    @field_validator('budget')
    @classmethod
    def validate_budget(cls, v):
        """Ensure budget has max 2 decimal places"""
        if v.as_tuple().exponent < -2:
            raise ValueError('Budget can have at most 2 decimal places')
        return v


class TaskResponse(BaseModel):
 
    id: str
    title: str
    description: str
    category: str
    budget: Decimal
    status: str
    creator_id: str
    assigned_to: Optional[str]
    deadline: Optional[datetime]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    # Creator information (populated via join)
    creator: Optional["TaskCreatorInfo"] = None

    class Config:
        from_attributes = True


class TaskCreatorInfo(BaseModel):

    id: str
    full_name: Optional[str]
    username: Optional[str]
    email: str

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):

    tasks: List[TaskResponse]
    total: int


class TaskSearchRequest(BaseModel):
   
    keyword: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    min_budget: Optional[Decimal] = None
    max_budget: Optional[Decimal] = None
    status: str = "open"

class SuccessResponse(BaseModel):
 
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):

    error: str
    detail: Optional[str] = None


# Update forward references
UserLoginResponse.model_rebuild()
TaskResponse.model_rebuild()
