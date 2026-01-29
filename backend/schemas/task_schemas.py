from pydantic import BaseModel
from typing import Optional
from backend.database.database_documents import Task_Categories
from datetime import datetime

class CreateTaskSchema(BaseModel):

    title: str
    description: str
    exp_time: Optional[str] = None
    category: Optional[Task_Categories] = None
    completed: Optional[bool] = False




class DeleteTaskSchema(BaseModel):

    task_id: str


class UpdateTaskSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    exp_time: Optional[str] = None
    category: Optional[Task_Categories] = None
    completed: Optional[bool] = None

