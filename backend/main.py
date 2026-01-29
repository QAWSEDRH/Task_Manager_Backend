from fastapi import FastAPI
from backend.routers.auth_router import auth_router
from backend.routers.task_router import task_router
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.database.database_documents import Task, User

app = FastAPI()

@app.on_event("startup")
async def start_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_databasedb
    await init_beanie(database=db, document_models=[Task, User])

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(task_router)
