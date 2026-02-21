from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from backend.schemas.auth_schemas import SignUpSchema, LoginSchema
from backend.database.database_documents import User
from datetime import timedelta
from backend.utils.limit import limiter
from fastapi import Request


import asyncio
import bcrypt

auth_router = APIRouter()



config = AuthXConfig()
config.JWT_SECRET_KEY = "secret"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
config.JWT_TOKEN_LOCATION = ["headers"]
config.JWT_HEADER_NAME = "Authorization"
config.JWT_HEADER_TYPE = "Bearer"
security = HTTPBearer()



auth = AuthX(config=config)




MAX_BCRYPT_BYTES = 72


async def hash_password(password: str) -> str:
    loop = asyncio.get_running_loop()
    hashed_bytes = await loop.run_in_executor(
        None,
        lambda: bcrypt.hashpw(password.encode("utf-8")[:MAX_BCRYPT_BYTES], bcrypt.gensalt())
    )
    return hashed_bytes.decode("utf-8")


async def verify_password(password: str, hashed: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: bcrypt.checkpw(password.encode("utf-8")[:MAX_BCRYPT_BYTES], hashed.encode("utf-8"))
    )


async def check_to_no_exist(email):
    existing_user = await User.find_one(User.email == email)
    if existing_user:
        raise HTTPException(400, "user already exists")


async def find_user(user_id: str):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user



@auth_router.post("/sign_up")
@limiter.limit("2/minute")
async def sign_up(creds: SignUpSchema,request:Request):
    await check_to_no_exist(creds.email)

    hashed_password = await hash_password(creds.password)

    new_user = User(
        name=creds.name,
        surname=creds.surname,
        email=creds.email,
        password=hashed_password
    )
    await new_user.insert()

    token = auth.create_access_token(uid=str(new_user.id))

    return {
        "message": "success",
        "access_token": token
    }

@limiter.limit("20/minute")
@auth_router.post("/login")
async def login(creds: LoginSchema,request:Request):
    # ищем по email только для логина
    user = await User.find_one(User.email == creds.email)
    if not user:
        raise HTTPException(404, "User not found")

    if not await verify_password(creds.password, user.password):
        raise HTTPException(400, "Incorrect password")

    token = auth.create_access_token(uid=str(user.id))




    return {
        "name": user.name,
        "access_token": token,
    }

@limiter.limit("20/minute")
@auth_router.get("/me")
async def protected_route(request:Request,payload = Depends(auth.access_token_required)):
    user = await find_user(payload["uid"])

    return {
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
    }










