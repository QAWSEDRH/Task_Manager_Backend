from pydantic import BaseModel
from typing import Optional
from backend.database.database_documents import TaskCategories
from datetime import datetime

class CreateTaskSchema(BaseModel):
    title: str
    description: str
    created_at:str
    exp_time: Optional[str] = None
    category: Optional[TaskCategories] = None
    completed: Optional[bool] = False




class DeleteTaskSchema(BaseModel):
    task_id: str


class UpdateTaskSchema(BaseModel):
    task_id: str

    title: Optional[str] = None
    description: Optional[str] = None
    exp_time: Optional[str] = None
    category: Optional[TaskCategories] = None
    completed: Optional[bool] = None

