from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from ai_model import stream_products
from db import (
    init_db,
    create_user,
    verify_user,
    record_message,
    record_recommendation,
    get_or_create_session,
)

import json
from fastapi.responses import StreamingResponse

app = FastAPI(
    title="API",
    description="A modern task management API built with FastAPI",
    version="1.0.0",
)

# initialize sqlite database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

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


class LoginInput(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
async def login(userdata: LoginInput):
    user = verify_user(userdata.email, userdata.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "message": "Login succesful back",
        "email": userdata.email,
        "user_id": user["id"],
        "fullname": user["full_name"],
    }


class SignupInput(BaseModel):
    fullname: str
    email: str
    password: str


@app.post("/auth/signup")
async def create_account(userdata: SignupInput):
    try:
        user_id = create_user(userdata.fullname, userdata.email, userdata.password)
    except Exception:
        raise HTTPException(status_code=409, detail="Email already exists")
    return {
        "message": "Account created succesfullly back",
        "email": userdata.email,
        "fullname": userdata.fullname,
        "user_id": user_id,
    }


@app.post("/agent_thinking")
async def show_thinking(think: dict):
    print("api received", think)
    return think


class ChatInput(BaseModel):
    prompt: str
    session_id: int


@app.post("/agent_asking")
async def ask(question: str):
    return question


@app.post("/chat")
async def send_chat(data: ChatInput):
    return {"message": "Use /chat/stream endpoint for chat responses"}


# streaming as search goes 1-1
@app.post("/chat/stream")
async def send_chat_stream(data: ChatInput):

    async def event_generator():
        get_or_create_session(data.session_id)
        record_message(data.session_id, "user", data.prompt)

        for product in stream_products(data.prompt, data.session_id):
            if isinstance(product, dict) and product.get("status") in {"need_user", "not_possible"}:
                record_message(
                    data.session_id,
                    "assistant",
                    json.dumps(product, ensure_ascii=True),
                )
            elif isinstance(product, dict) and product.get("type") == "status":
                pass
            elif isinstance(product, dict):
                record_recommendation(data.session_id, product)

            yield f"data: {json.dumps(product)}\n\n"

        print("SENDING DONE EVENT")
        yield f"data: {json.dumps({'status': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")