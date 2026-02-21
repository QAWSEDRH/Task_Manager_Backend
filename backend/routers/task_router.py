from beanie import PydanticObjectId
from backend.utils.limit import limiter
from backend.schemas.task_schemas import CreateTaskSchema,DeleteTaskSchema,UpdateTaskSchema
from backend.database.database_documents import User,Task,TaskCategories
from fastapi import Request
from fastapi import APIRouter,HTTPException,Depends
from backend.routers.auth_router import auth
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.schemas.task_schemas import CreateTaskSchema, UpdateTaskSchema

class CreateTasksSchema(BaseModel):
    tasks: List[CreateTaskSchema] = Field(..., max_items=20)

class UpdateTasksSchema(BaseModel):
    tasks: List[UpdateTaskSchema] = Field(..., max_items=20)



task_router = APIRouter()




async def get_current_user(payload = Depends(auth.access_token_required)):
    user_id = getattr(payload, "sub", None)
    if not user_id:
        raise HTTPException(401, "Invalid token: no user id")

    user = await User.get(user_id)

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

@limiter.limit("20/minute")
@task_router.post("/task/create")
async def create_task(task_data:CreateTaskSchema,request:Request,user: User = Depends(get_current_user)):
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        created_at=task_data.created_at,
        exp_time=task_data.exp_time,
        creator_id= user.id,
        category=task_data.category or TaskCategories.no_category_task,
        completed=task_data.completed or False
    )
    await new_task.insert()

    return {"message": "success", "task_id": str(new_task.id)}



@limiter.limit("20/minute")
@task_router.delete("/task/delete")
async def delete_task(task_data:DeleteTaskSchema,request:Request, user:User = Depends(get_current_user)):
    task = await find_task_by_id(task_data.task_id)

    if task.creator_id != user.id:
        raise HTTPException(403, "Permission denied")

    await task.delete()
    return {"message":"task deleted"}


@limiter.limit("20/minute")
@task_router.patch("/task/update")
async def update_task(data: UpdateTaskSchema,request:Request, user: User = Depends(get_current_user)):
    task = await find_task_by_id(data.task_id)

    if task.creator_id != user.id:
        raise HTTPException(403, "Permission denied")

    update_data = data.model_dump(exclude_unset=True)

    update_data.pop("task_id", None)

    allowed = {"title", "description", "exp_time", "category", "completed"}
    for key, value in update_data.items():
        if key in allowed:
            setattr(task, key, value)

    await task.save()
    return {"message": "task updated successfully", "updated_fields": update_data}



@limiter.limit("20/minute")
@task_router.get("/task/{skip}/{limit}")
async def get_tasks_paginated(skip: int,request:Request, limit: int, user: User = Depends(get_current_user)):
    tasks = await (Task.find(Task.creator_id == user.id)
                   .sort(Task.created_at)
                   .skip(skip)
                   .limit(limit)
                   .to_list()
                   )
    return [task.model_dump(by_alias=True) for task in tasks]



@limiter.limit("20/minute")
async def get_tasks(user_id, date, skip: int, limit: int,request:Request):
    tasks = await (Task.find(
        Task.creator_id == user_id,
        {"created_at": {"$regex": f"^{date}"}}  # Используем MongoDB regex вместо startswith
    )
    .sort(Task.created_at)
    .skip(skip)
    .limit(limit)
    .to_list()
    )
    return [task.model_dump(by_alias=True) for task in tasks]





#date format -> ISO 8601
@limiter.limit("20/minute")
@task_router.get("/task/{date}/{skip}/{limit}")
async def get_tasks_paginated(date:str,skip:int,limit:int,request:Request, user: User = Depends(get_current_user)):
    tasks = await get_tasks(user.id, date, skip, limit)
    return tasks




@limiter.limit("20/minute")
@task_router.post("/tasks/create_bulk")
async def create_tasks_bulk(data: CreateTasksSchema, request: Request, user: User = Depends(get_current_user)):
    if len(data.tasks) > 20:
        raise HTTPException(400, "Maximum 20 tasks per request")

    created_tasks = []
    for task_data in data.tasks:
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            created_at=task_data.created_at,
            exp_time=task_data.exp_time,
            creator_id=user.id,
            category=task_data.category or TaskCategories.no_category_task,
            completed=task_data.completed or False
        )
        await new_task.insert()
        created_tasks.append(str(new_task.id))

    return {"message": "success", "task_ids": created_tasks}




@limiter.limit("20/minute")
@task_router.patch("/tasks/update_bulk")
async def update_tasks_bulk(data: UpdateTasksSchema, request: Request, user: User = Depends(get_current_user)):
    if len(data.tasks) > 20:
        raise HTTPException(400, "Maximum 20 tasks per request")

    updated_tasks = []

    for task_data in data.tasks:
        task = await find_task_by_id(task_data.task_id)

        if task.creator_id != user.id:
            continue  # Игнорируем задачи, которые не принадлежат пользователю

        update_data = task_data.model_dump(exclude_unset=True)
        update_data.pop("task_id", None)

        allowed = {"title", "description", "exp_time", "category", "completed"}
        for key, value in update_data.items():
            if key in allowed:
                setattr(task, key, value)

        await task.save()
        updated_tasks.append({"task_id": str(task.id), "updated_fields": list(update_data.keys())})

    return {"message": "tasks updated successfully", "updated_tasks": updated_tasks}






