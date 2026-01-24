from pydantic import BaseModel

class SignUpSchema(BaseModel):
    name:str
    surname:str
    email:str
    password:str

class LoginSchema(BaseModel):
    name:str
    password:str
