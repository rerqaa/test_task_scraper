import os
import re
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.scraper_db
collection = db.scans
app = FastAPI(title="Website Scraper API")

async def count_word(url, word):
    async with httpx.AsyncClient(verify=False) as http_client:
        response = await http_client.get(url)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=' ', strip=True)
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        matches = pattern.findall(text)
        return len(matches)

class ScanRequest(BaseModel):
    url: str
    word: str

class ScanResponse(BaseModel):
    id: str
    url: str
    word: str
    count: int
    created_at: datetime
    updated_at: datetime

class ScanUpdate(BaseModel):
    url: Optional[str] = None
    word: Optional[str] = None
    count: Optional[int] = None

def serialize_doc(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@app.post("/scan", response_model=ScanResponse)
async def create_scan(request: ScanRequest):
    try:
        count = await count_word(request.url, request.word)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    now = datetime.now(timezone.utc)
    doc = {
        "url": request.url,
        "word": request.word,
        "count": count,
        "created_at": now,
        "updated_at": now
    }
    result = await collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@app.get("/scans", response_model=List[ScanResponse])
async def get_scans(url: Optional[str] = Query(None), word: Optional[str] = Query(None)):
    query = {}
    if url:
        query["url"] = url
    if word:
        query["word"] = word
        
    cursor = collection.find(query)
    scans = await cursor.to_list()
    return [serialize_doc(doc) for doc in scans]

@app.get("/scans/{id}", response_model=ScanResponse)
async def get_scan(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    doc = await collection.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Scan not found")
    return serialize_doc(doc)

@app.post("/scans/{id}/rescan", response_model=ScanResponse)
async def rescan(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    doc = await collection.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Scan not found")
    try:
        count = await count_word(doc["url"], doc["word"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    now = datetime.now(timezone.utc)
    update_data = {
        "count": count,
        "updated_at": now
    }
    await collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    doc.update(update_data)
    return serialize_doc(doc)

@app.patch("/scans/{id}", response_model=ScanResponse)
async def update_scan(id: str, update: ScanUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    doc = await collection.find_one({"_id": ObjectId(id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    update_data = update.model_dump(exclude_unset=True) if hasattr(update, "model_dump") else update.dict(exclude_unset=True)
    if not update_data:
        return serialize_doc(doc)
        
    update_data["updated_at"] = datetime.now(timezone.utc)
    await collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    doc.update(update_data)
    return serialize_doc(doc)
