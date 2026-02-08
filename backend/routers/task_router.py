from beanie import PydanticObjectId

from backend.schemas.task_schemas import CreateTaskSchema,DeleteTaskSchema,UpdateTaskSchema
from backend.database.database_documents import User,Task,TaskCategories

from fastapi import APIRouter,HTTPException,Depends
from backend.routers.auth_router import auth



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


@task_router.post("/task/create")
async def create_task(task_data:CreateTaskSchema,user: User = Depends(get_current_user)):
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




@task_router.delete("/task/delete")
async def delete_task(task_data:DeleteTaskSchema, user:User = Depends(get_current_user)):
    task = await find_task_by_id(task_data.task_id)

    if task.creator_id != user.id:
        raise HTTPException(403, "Permission denied")

    await task.delete()
    return {"message":"task deleted"}



@task_router.patch("/task/update")
async def update_task(data: UpdateTaskSchema, user: User = Depends(get_current_user)):
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




@task_router.get("/task/{skip}/{limit}")
async def get_tasks_paginated(skip: int, limit: int, user: User = Depends(get_current_user)):
    tasks = await (Task.find(Task.creator_id == user.id)
                   .sort(Task.created_at)
                   .skip(skip)
                   .limit(limit)
                   .to_list()
                   )
    return [task.model_dump(by_alias=True) for task in tasks]



async def get_first_on_tasks(user_id):
    tasks = await ((Task.find(Task.creator_id == user_id)
                   .sort(Task.created_at)
                   .skip(0)
                   .limit(10)
                   .to_list()
                   ))
    return [task.model_dump(by_alias=True) for task in tasks]






