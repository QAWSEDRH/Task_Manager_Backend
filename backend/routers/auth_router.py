from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig
from fastapi import APIRouter
from fastapi.security import HTTPBearer
from backend.schemas.auth_schemas import SignUpSchema, LoginSchema
from backend.database.database_documents import User


import asyncio
import bcrypt

auth_router = APIRouter()


async def find_user(name: str):
    user = await User.find_one(User.name == name)
    if not user:
        raise HTTPException(404, "User not found")
    return user




config = AuthXConfig()
config.JWT_SECRET_KEY = "secret"
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


async def check_to_no_exist(name: str):
    existing_user = await User.find_one(User.name == name)
    if existing_user:
        raise HTTPException(400, "user already exists")


@auth_router.post("/sign_up")
async def sign_up(creds: SignUpSchema):
    await check_to_no_exist(creds.name)

    hashed_password = await hash_password(creds.password)

    new_user = User(
        name=creds.name,
        surname=creds.surname,
        email=creds.email,
        password=hashed_password
    )
    await new_user.insert()

    token = auth.create_access_token(uid=creds.name)

    return {
        "message": "success",
        "access_token": token
    }


@auth_router.post("/login")
async def login(creds: LoginSchema):
    user = await find_user(creds.name)

    if not await verify_password(creds.password, user.password):
        raise HTTPException(400, "Incorrect password")

    token = auth.create_access_token(uid=creds.name)

    return {"name": creds.name,"access_token": token}






@auth_router.get("/protected")
async def protected_route(user = Depends(auth.access_token_required)):
    return {"message": "OK"}



__all__ = ["auth_router", "auth", "find_user"]



