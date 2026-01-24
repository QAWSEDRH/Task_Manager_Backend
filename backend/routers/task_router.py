from unicodedata import category

from beanie import PydanticObjectId

from backend.schemas.task_schemas import CreateTaskSchema,DeleteTaskSchema,UpdateTaskSchema
from backend.database.database_documents import User,Task,Task_Categories,Complete_Status
from backend.routers.auth_router import find_user
from fastapi import APIRouter,HTTPException,Depends
from backend.routers.auth_router import auth
from typing import Any


task_router = APIRouter()




async def get_current_user(current: Any = Depends(auth.access_token_required)):

    user = await User.find_one(User.name == current.sub)
    if not user:
        raise HTTPException(404, "User not found")
    return user


async def find_task_by_id(task_id: str):
    try:
        oid = PydanticObjectId(task_id)
    except:
        raise HTTPException(400,"invalid id")
    task = await Task.get(oid)
    if not task:
        raise HTTPException(404,"task not found")
    return task


@task_router.post("/task/create")
async def create_task(task_data:CreateTaskSchema,user: User = Depends(get_current_user)):
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        exp_time=task_data.exp_time or "",
        creator_name=user.name,
        category=task_data.category or Task_Categories.no_category_task,
        completed=task_data.completed or Complete_Status.not_completed
    )
    await new_task.insert()

    return {"message": "success", "task_id": str(new_task.id)}




@task_router.delete("/task/delete")
async def delete_task(task_data:DeleteTaskSchema, user:User = Depends(get_current_user)):
    task = await find_task_by_id(task_data.task_id)
    await task.delete()
    return {"message":"task deleted"}



@task_router.patch("/task/update")
async def update_task(data: UpdateTaskSchema, user: User = Depends(get_current_user)):
    task = await find_task_by_id(data.task_id)

    if task.creator_name != user.name:
        raise HTTPException(403, "Permission denied")

    update_data = data.dict(exclude_unset=True)
    update_data.pop("task_id", None)

    allowed = {"title", "description", "exp_time", "category", "completed"}
    for key, value in update_data.items():
        if key in allowed:
            setattr(task, key, value)

    await task.save()
    return {"message": "task updated successfully", "updated_fields": update_data}




