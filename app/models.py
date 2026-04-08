from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

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
    
# # Sprint 3 changes(Skil-17)

class ApplicantDecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(accepted|rejected)$")


class ApplicantDecisionResponse(BaseModel):
    message: str
    application_id: str
    task_id: str
    applicant_id: str
    status: str
    
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

# sprint 3 Skil-18 changes
class SkillProfileCreateRequest(BaseModel):
    skills: List[str] = Field(..., min_length=1)
    experience: str = Field(..., min_length=1, max_length=2000)
    bio: str = Field(..., min_length=1, max_length=500)

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v):
        cleaned = [skill.strip() for skill in v if skill and skill.strip()]
        if not cleaned:
            raise ValueError("At least one skill is required")
        return cleaned


class SkillProfileResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    username: Optional[str]
    bio: Optional[str]
    skills: Optional[List[str]]
    experience: Optional[str]
    student_id: Optional[str]
    university: Optional[str]
    portfolio_url: Optional[str] = None          # Skil-20 updates 
    portfolio_filename: Optional[str] = None
    portfolio_type: Optional[str] = None
    portfolio_link: Optional[str] = None         # Skil-20 updates 
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
# Skil-19
class SkillProfileUpdateRequest(BaseModel):
    skills: List[str] = Field(..., min_length=1)
    experience: str = Field(..., min_length=1, max_length=2000)
    bio: str = Field(..., min_length=1, max_length=500)

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v):
        cleaned = [skill.strip() for skill in v if skill and skill.strip()]
        if not cleaned:
            raise ValueError("At least one skill is required")
        return cleaned
   
# Skil-20 updates 
class PortfolioLinkRequest(BaseModel):
    portfolio_link: str = Field(..., min_length=1, max_length=1000)