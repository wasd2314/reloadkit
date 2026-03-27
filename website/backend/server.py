from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class App(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    icon_name: str
    description: str
    url: str
    download_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AppCreate(BaseModel):
    name: str
    category: str
    icon_name: str
    description: str
    url: str

class AppUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    icon_name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


# Seed initial data
@app.on_event("startup")
async def seed_data():
    # Check if apps collection is empty
    count = await db.apps.count_documents({})
    if count == 0:
        initial_apps = [
            {"id": str(uuid.uuid4()), "name": "Discord", "category": "Social Media", "icon_name": "SiDiscord", "description": "Voice, video and text chat app.", "url": "https://discord.com/api/download?platform=win", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "Medal", "category": "Gaming", "icon_name": "SiMedal", "description": "Free game recording and clipping software.", "url": "https://medal.tv/download", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "Spotify", "category": "Other", "icon_name": "SiSpotify", "description": "Music streaming service.", "url": "https://download.scdn.co/SpotifySetup.exe", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "PotPlayer", "category": "Other", "icon_name": "FaPlayCircle", "description": "Lightweight media player with hardware acceleration.", "url": "https://t1.daumcdn.net/potplayer/PotPlayer/Version/Latest/PotPlayerSetup64.exe", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "MPV Player", "category": "Other", "icon_name": "FaPlay", "description": "Ultra-lightweight minimalist media player.", "url": "https://mpv.io/installation/", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "WinRAR", "category": "Other", "icon_name": "FaFileArchive", "description": "Powerful file archiver and compression tool.", "url": "https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-713.exe", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "Notepad++", "category": "Other", "icon_name": "FaFileCode", "description": "Free source code and text editor.", "url": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.9.3/npp.8.9.3.Installer.x64.exe", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "OBS Studio", "category": "Other", "icon_name": "SiObsstudio", "description": "Free streaming and recording software.", "url": "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-32.1.0-Windows-Installer.exe", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "Firefox", "category": "Other", "icon_name": "SiFirefox", "description": "Fast, private, and free web browser.", "url": "https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "Steam", "category": "Gaming", "icon_name": "SiSteam", "description": "Ultimate destination for playing games.", "url": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "Epic Games", "category": "Gaming", "icon_name": "SiEpicgames", "description": "Download and play PC games.", "url": "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "BakkesMod", "category": "Gaming", "icon_name": "FaGamepad", "description": "Rocket League modding and training tool.", "url": "https://github.com/bakkesmodorg/BakkesModInjectorC/releases/latest/download/BakkesModSetup.zip", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "FiveM", "category": "Gaming", "icon_name": "FaCarCrash", "description": "Play GTA V on customized multiplayer servers.", "url": "https://runtime.fivem.net/client/FiveM.exe", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "µTorrent", "category": "Other", "icon_name": "SiUtorrent", "description": "A very tiny BitTorrent client.", "url": "https://www.utorrent.com/downloads/complete/track/stable/os/win/", "download_count": 0, "created_at": datetime.now(timezone.utc).isoformat()}
        ]
        await db.apps.insert_many(initial_apps)
        logger.info(f"Seeded {len(initial_apps)} initial apps")


# Routes
@api_router.get("/")
async def root():
    return {"message": "Software Download Hub API"}

@api_router.get("/apps", response_model=List[App])
async def get_apps():
    apps = await db.apps.find({}, {"_id": 0}).to_list(1000)
    for app in apps:
        if isinstance(app.get('created_at'), str):
            app['created_at'] = datetime.fromisoformat(app['created_at'])
    return apps

@api_router.post("/apps", response_model=App)
async def create_app(input: AppCreate):
    app_dict = input.model_dump()
    app_obj = App(**app_dict)
    
    doc = app_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.apps.insert_one(doc)
    return app_obj

@api_router.put("/apps/{app_id}", response_model=App)
async def update_app(app_id: str, input: AppUpdate):
    existing = await db.apps.find_one({"id": app_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="App not found")
    
    update_data = {k: v for k, v in input.model_dump().items() if v is not None}
    if update_data:
        await db.apps.update_one({"id": app_id}, {"$set": update_data})
    
    updated = await db.apps.find_one({"id": app_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return App(**updated)

@api_router.delete("/apps/{app_id}")
async def delete_app(app_id: str):
    result = await db.apps.delete_one({"id": app_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="App not found")
    return {"message": "App deleted successfully"}

@api_router.post("/apps/{app_id}/download")
async def increment_download(app_id: str):
    result = await db.apps.update_one(
        {"id": app_id},
        {"$inc": {"download_count": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="App not found")
    
    app = await db.apps.find_one({"id": app_id}, {"_id": 0})
    if isinstance(app.get('created_at'), str):
        app['created_at'] = datetime.fromisoformat(app['created_at'])
    return App(**app)

@api_router.get("/stats")
async def get_stats():
    total_downloads = await db.apps.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$download_count"}}}
    ]).to_list(1)
    
    total = total_downloads[0]['total'] if total_downloads else 0
    app_count = await db.apps.count_documents({})
    
    return {
        "total_apps": app_count,
        "total_downloads": total
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
