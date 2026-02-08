from beanie import Document
from enum import Enum
from datetime import datetime
from pydantic import Field
from bson import ObjectId
from beanie import PydanticObjectId


class User(Document):
    name: str
    surname: str
    email: str
    password: str

    class Settings:
        collection = "users"

    class Config:
        json_encoders = {
            ObjectId: str,
            PydanticObjectId: str,
        }


class TaskCategories(str, Enum):
    school_task = "school_task"
    house_task = "house_task"
    own_bussiness_task = "own_bussiness_task"
    no_category_task = "no_category_task"


from beanie import Document
from pydantic import Field
from datetime import datetime


class Task(Document):

    title: str
    description: str
    created_at: str
    exp_time: str
    creator_id: PydanticObjectId
    category: str = "no_category_task"
    completed: bool = False

    class Settings:
        name = "tasks"
