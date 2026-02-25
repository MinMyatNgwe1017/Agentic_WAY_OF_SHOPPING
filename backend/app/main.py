from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(
    title="API",
    description="A modern task management API built with FastAPI",
    version="1.0.0"
)

# Configure CORS for React frontend (Sufiyan, this block connects the frontend with the back-end)
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

#test
@app.get("/test")
async def test():
    return {"message":"This is test"}