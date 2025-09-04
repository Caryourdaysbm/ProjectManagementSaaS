from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = Field(pattern="^(Admin|Member)$")

class UserCreate(UserBase):
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    class Config:
        from_attributes = True

class OrganizationCreate(BaseModel):
    org_name: str
    subscription_tier: str = "free"
    admin_name: str
    admin_email: EmailStr
    password: str

class OrganizationOut(BaseModel):
    id: int
    name: str
    subscription_tier: str
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending", pattern="^(pending|in_progress|done)$")
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    project_id: int
    assigned_user_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(pending|in_progress|done)$")
    due_date: Optional[date] = None
    assigned_user_id: Optional[int] = None

class TaskOut(TaskBase):
    id: int
    project_id: int
    assigned_user_id: Optional[int]
    class Config:
        from_attributes = True

class MetricsOut(BaseModel):
    total_projects: int
    total_tasks: int
    completed_tasks: int

class ProjectAggOut(BaseModel):
    project_id: int
    title: str
    total_tasks: int
    completed_tasks: int
