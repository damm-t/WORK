"""
FastAPI Web Server for Instagram Extractor & Quant Abstractor
============================================================
Runs an interactive web UI and REST API for downloading, transcribing,
and abstracting Instagram Reels and videos.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from instagram_extractor.core import (
    extract_instagram_media,
    process_instagram_url
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Instagram Quant Intelligence Extractor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExtractRequest(BaseModel):
    url: str
    transcribe: Optional[bool] = True

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = BASE_DIR / "templates" / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    return index_file.read_text(encoding="utf-8")

@app.post("/api/extract-only")
async def api_extract_only(req: ExtractRequest):
    """Fast extraction of raw CDN streams without downloading."""
    try:
        data = extract_instagram_media(req.url)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/process")
async def api_process(req: ExtractRequest):
    """Full pipeline: extract, download, audio conversion, transcription, quant abstraction."""
    try:
        result = process_instagram_url(req.url, output_dir=str(OUTPUT_DIR), transcribe=req.transcribe)
        
        # Convert local filepaths to relative API URLs
        slug = result["slug"]
        result["media_urls"] = {
            "video_url": f"/api/media/{slug}.mp4",
            "audio_url": f"/api/media/{slug}.mp3",
            "thumbnail_url": f"/api/media/{slug}.jpg" if (OUTPUT_DIR / f"{slug}.jpg").exists() else None,
            "transcript_url": f"/api/media/{slug}_transcript.txt",
            "metadata_url": f"/api/media/{slug}_metadata.json"
        }
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/media/{filename}")
async def serve_media(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        # Check in downloads as fallback
        dl_path = BASE_DIR / "downloads" / filename
        if dl_path.exists():
            return FileResponse(str(dl_path))
        raise HTTPException(status_code=404, detail="Media file not found")
    return FileResponse(str(file_path))

@app.get("/api/preset/{slug}")
async def get_preset(slug: str):
    """Returns pre-extracted data for the 3 demo reels."""
    # Check if output exists
    meta_path = OUTPUT_DIR / f"{slug}_metadata.json"
    if meta_path.exists():
        import json
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["media_urls"] = {
                "video_url": f"/api/media/{slug}.mp4",
                "audio_url": f"/api/media/{slug}.mp3",
                "thumbnail_url": f"/api/media/{slug}.jpg" if (OUTPUT_DIR / f"{slug}.jpg").exists() else None,
                "transcript_url": f"/api/media/{slug}_transcript.txt",
                "metadata_url": f"/api/media/{slug}_metadata.json"
            }
            return {"status": "success", "result": data}
            
    # Map reel aliases
    mapping = {
        "reel_1": "https://www.instagram.com/reel/DeUW_vslUI8/",
        "reel_2": "https://www.instagram.com/reel/DedM-fnN7vS/",
        "reel_3": "https://www.instagram.com/reel/Dd-ZeUxvFWS/",
        "DeUW_vslUI8": "https://www.instagram.com/reel/DeUW_vslUI8/",
        "DedM-fnN7vS": "https://www.instagram.com/reel/DedM-fnN7vS/",
        "Dd-ZeUxvFWS": "https://www.instagram.com/reel/Dd-ZeUxvFWS/"
    }
    target_url = mapping.get(slug)
    if not target_url:
        raise HTTPException(status_code=404, detail="Preset not found")
        
    result = process_instagram_url(target_url, output_dir=str(OUTPUT_DIR), transcribe=True)
    res_slug = result["slug"]
    result["media_urls"] = {
        "video_url": f"/api/media/{res_slug}.mp4",
        "audio_url": f"/api/media/{res_slug}.mp3",
        "thumbnail_url": f"/api/media/{res_slug}.jpg" if (OUTPUT_DIR / f"{res_slug}.jpg").exists() else None,
        "transcript_url": f"/api/media/{res_slug}_transcript.txt",
        "metadata_url": f"/api/media/{res_slug}_metadata.json"
    }
    return {"status": "success", "result": result}

if __name__ == "__main__":
    port = int(os.environ.get("EXTRACTOR_PORT", 8095))
    print(f"Starting Instagram Quant Extractor Web UI on http://localhost:{port}")
    uvicorn.run("instagram_extractor.web_server:app", host="0.0.0.0", port=port, reload=False)
