from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time

app = FastAPI()

class Equipment(BaseModel):
    primary_left_wep: int = 0
    primary_right_wep: int = 0
    secondary_left_wep: int = 0
    secondary_right_wep: int = 0
    tertiary_left_wep: int = 0
    tertiary_right_wep: int = 0
    primary_arrow: int = 0
    primary_bolt: int = 0
    secondary_arrow: int = 0
    secondary_bolt: int = 0
    tertiary_arrow: int = 0
    tertiary_bolt: int = 0
    helmet: int = 0
    armor: int = 0
    gauntlet: int = 0
    leggings: int = 0
    hair: int = 0
    accessory_1: int = 0
    accessory_2: int = 0
    accessory_3: int = 0
    accessory_4: int = 0
    accessory_5: int = 0

class PlayerStats(BaseModel):
    name: str
    level: int
    reinforce_level: int = 0
    health: int = 0
    max_hp: int = 0
    max_fp: int = 0
    max_stamina: int = 0
    character_type: int = 0
    team_type: int = 0
    vigor: int = 0
    mind: int = 0
    endurance: int = 0
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    faith: int = 0
    arcane: int = 0
    equipment: Equipment = Equipment()

class Session(BaseModel):
    username: str
    message: str
    password: str
    level: int
    stats: PlayerStats

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
    allow_origins=["*"],  # allow_origins=["https://2pz.github.io"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
