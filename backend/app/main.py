from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from ai_model import search_information,extract_and_think
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

@app.post("/agent_thinking")
async def show_thinking(think:dict):
    print("api received",think)
    return think
    
class ChatInput(BaseModel):
    prompt: str
    session_id:int=30


@app.post("/agent_asking")
async def ask(question:str):
    
    return question

@app.post("/chat")
async def send_chat(data: ChatInput):
    extract_and_think(data.prompt,data.session_id)
    
    
    print("in the fastapi")
    return {"msg": data.prompt}
