from beanie import Document
from enum import Enum
from datetime import datetime
from beanie import PydanticObjectId
from pydantic import Field


class User(Document):
    name:str
    surname:str
    email:str
    password:str

    class Settings:
        collection = "users"

class Task_Categories(str,Enum):
    school_task = "school_task"
    house_task = "house_task"
    own_bussiness_task = "own_bussiness_task"
    no_category_task  = "no_category_task"




class Task(Document):
    title:str
    description:str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    exp_time:str
    creator_id: PydanticObjectId
    category: Task_Categories = Task_Categories.no_category_task
    completed: bool = False



    class Settings:
        collection = "tasks"
