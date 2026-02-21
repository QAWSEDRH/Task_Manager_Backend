from fastapi import FastAPI, Request
from backend.routers.auth_router import auth_router
from backend.routers.task_router import task_router
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.database.database_documents import Task, User
from backend.utils.logger_settings import logger

# --- rate limiter ---
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from backend.utils.limit import limiter


app = FastAPI()

# add limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


# --- Rate Limit error handler ---
@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )


# --- Logger ---
@app.middleware("http")
async def logger_а(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response


# --- MongoDB Start ---
@app.on_event("startup")
async def start_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_databasedb
    await init_beanie(database=db, document_models=[Task, User])


# --- Routers ---
app.include_router(auth_router)
app.include_router(task_router)
