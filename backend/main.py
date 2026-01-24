from fastapi import FastAPI
from backend.routers.auth_router import auth_router
from backend.database.database_settings import router
from backend.routers.task_router import task_router



app = FastAPI()




app.include_router(auth_router)
app.include_router(router)
app.include_router(task_router)
