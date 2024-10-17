from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

sessions = []

class Session(BaseModel):
    username: str
    message: str
    password: str

class RemoveSession(BaseModel):
    username: str
    action: str

@app.get("/")
async def get_sessions():
    return sessions

@app.get("/sessions.json")
async def get_sessions_json():
    return sessions

@app.post("/api/add_session")
async def add_session(session: Session):
    for existing_session in sessions:
        if existing_session.username == session.username:
            raise HTTPException(status_code=400, detail="Username already exists")
    sessions.append(session)
    return {"message": "Session added successfully"}

@app.post("/api/remove_session")
async def remove_session(remove: RemoveSession):
    if remove.action != "remove":
        raise HTTPException(status_code=400, detail="Invalid action")
    for i, session in enumerate(sessions):
        if session.username == remove.username:
            del sessions[i]
            return {"message": "Session removed successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/ping")
async def ping():
    return {"status": "ok"}

# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://2pz.github.io"],  # Replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
