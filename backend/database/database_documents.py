from beanie import Document
from enum import Enum

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

class Complete_Status(str,Enum):
    completed = "completed"
    not_completed = "not_completed"


class Task(Document):
    title:str
    description:str
    exp_time:str
    creator_name:str
    category: Task_Categories = Task_Categories.no_category_task
    completed: bool = False



    class Settings:
        collection = "tasks"
