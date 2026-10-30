from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    task_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.pending

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    comments: list[Comment] = []
    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: TaskStatus