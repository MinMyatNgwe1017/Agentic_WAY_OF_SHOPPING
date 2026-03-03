from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(
    title="API",
    description="A modern task management API built with FastAPI",
    version="1.0.0",
)

# (Sufiyan, this block connects the frontend with the back-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "This is root", "version": "1.0.0"}


# test
@app.get("/test")
async def test():
    return {"message": "This is test"}


class LoginInput(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
async def login(userdata: LoginInput):

    return {"message": "Login succesful back", "email": userdata.email}


class SignupInput(BaseModel):
    fullname: str
    email: str
    password: str


@app.post("/auth/signup")
async def create_account(userdata: SignupInput):

    return {
        "message": "Account created succesfullly back",
        "email": userdata.email,
        "fullname": userdata.fullname,
        "password": userdata.password,
    }


class ChatInput(BaseModel):
    prompt: str


@app.post("/chat")
def send_chat(data: ChatInput):
    print(data)
    return {"msg": data.prompt}
