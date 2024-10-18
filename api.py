from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time

app = FastAPI()

class Session(BaseModel):
    username: str
    message: str
    password: str
    level: int
    stats: Dict[str, int]

class RemoveSession(BaseModel):
    username: str
    action: str
    

@app.get("/")
async def get_sessions():
    return sessions

@app.get("/sessions.json")
async def get_sessions_json():
    return sessions

sessions = []
last_update_time = time.time()
update_event = asyncio.Event()

@app.post("/api/add_session")
async def add_session(session: Session):
    global last_update_time, update_event
    sessions.append(session)
    last_update_time = time.time()
    update_event.set()
    update_event.clear()
    return {"message": "Session added successfully"}

@app.post("/api/remove_session")
async def remove_session(remove: RemoveSession):
    global last_update_time, update_event
    if remove.action != "remove":
        raise HTTPException(status_code=400, detail="Invalid action")
    for i, session in enumerate(sessions):
        if session.username == remove.username:
            del sessions[i]
            last_update_time = time.time()
            update_event.set()
            update_event.clear()
            return {"message": "Session removed successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/long_poll")
async def long_poll(last_update: float, background_tasks: BackgroundTasks):
    global last_update_time, update_event
    
    if last_update < last_update_time:
        return {"updates": True, "sessions": sessions, "last_update": last_update_time}
    
    async def wait_for_update():
        try:
            await asyncio.wait_for(update_event.wait(), timeout=30)
        except asyncio.TimeoutError:
            pass
    
    background_tasks.add_task(wait_for_update)
    await wait_for_update()
    
    if last_update < last_update_time:
        return {"updates": True, "sessions": sessions, "last_update": last_update_time}
    else:
        return {"updates": False}

# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://2pz.github.io"],  # allow_origins=["https://2pz.github.io"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
