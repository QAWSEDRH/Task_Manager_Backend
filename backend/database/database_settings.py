import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi import APIRouter
from backend.database.database_documents import Task,User

router = APIRouter()

#подключение к базе данных монго

@router.on_event("startup")
async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_databasedb # подключение к базе данных


    #подключение к beanie
    await init_beanie(database=db, document_models=[Task,User])
