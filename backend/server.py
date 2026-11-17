import os
import sys
import json
import base64
import uuid
import urllib.request
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import Optional, Dict, Any
from backend.pipeline import run_pipeline, DB_PATH, _load_db, _save_db
from backend.modules.tts_engine import get_voice_list, generate_voiceover
from backend.modules.ai_brain import SUPPORTED_AI_MODELS
from backend.modules.trend_hunter import get_live_radar_trends
from backend.modules.video_renderer import get_bgm_list

app = FastAPI(title="AI Beauty Marketing Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage")
RAW_ASSETS_DIR = os.path.join(STORAGE_DIR, "raw_assets")
UPLOADS_DIR = os.path.join(RAW_ASSETS_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

def _resolve_product_image(image_input: Optional[str]) -> Optional[str]:
    if not image_input or not str(image_input).strip():
        return None
    image_input = str(image_input).strip()
    
    # 1. Base64 data URL
    if ";base64," in image_input or image_input.startswith("data:image/"):
        try:
            header, b64_str = image_input.split(";base64,")
            ext = ".png" if "png" in header.lower() else (".webp" if "webp" in header.lower() else ".jpg")
            filename = f"upload_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(UPLOADS_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(b64_str))
            return file_path
        except Exception as e:
            print(f"Failed to decode base64 image: {e}")
            return None
            
    # 2. Remote HTTP / HTTPS URL
    if image_input.startswith("http://") or image_input.startswith("https://"):
        try:
            req = urllib.request.Request(
                image_input,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                filename = f"url_{uuid.uuid4().hex[:8]}.jpg"
                file_path = os.path.join(UPLOADS_DIR, filename)
                with open(file_path, "wb") as f:
                    f.write(content)
                return file_path
        except Exception as e:
            print(f"Failed to download remote product image {image_input}: {e}")
            return None
            
    # 3. Already a local file path
    if os.path.exists(image_input):
        return image_input
        
    # 4. Check relative to UPLOADS_DIR
    check_up = os.path.join(UPLOADS_DIR, os.path.basename(image_input))
    if os.path.exists(check_up):
        return check_up
        
    return None

class ScriptGenerateRequest(BaseModel):
    product_prompt: str
    category: str = "beauty_skincare"
    target_gender: str = "women"
    target_duration: int = 30
    tone: str = "emotional_hook"

class PreviewScriptAudioRequest(BaseModel):
    text: str
    voice_key: str = "swara_influencer"

class GenerateRequest(BaseModel):
    product_prompt: str
    category: str = "beauty_skincare"
    target_gender: str = "women"
    language: str = "roman_urdu"
    action_type: str = "face_application"
    voice_key: str = "swara_influencer"
    bgm_track: str = "lofi_chill"
    avatar_character: str = "ayesha_derm"
    avatar_layout: str = "multi_angle"
    heygen_api_key: Optional[str] = None
    target_duration: int = 30
    ai_model: str = "auto_smart"
    api_key: Optional[str] = None
    date_range_type: str = "last_7_days"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    product_image_data: Optional[str] = None
    custom_script: Optional[Dict[str, Any]] = None
    supermodel_id: Optional[str] = None
    hairstyle: Optional[str] = "Natural"
    wardrobe: Optional[str] = "Standard"
    video_engine_provider: Optional[str] = "local" # "replicate", "fal", "hedra", "local"
    video_engine_model: Optional[str] = "kling" # "kling", "minimax", "wan"
    video_engine_key: Optional[str] = None

class AIVideoRequest(BaseModel):
    prompt: str
    image_path: Optional[str] = None
    provider: str = "replicate"
    model: str = "kling"
    api_key: Optional[str] = None
    duration: int = 5
    aspect_ratio: str = "9:16"

class UploadImageRequest(BaseModel):
    image_data: str
    filename: Optional[str] = None

class TestVoiceRequest(BaseModel):
    voice_key: str
    sample_text: str = "As-salamu alaykum! Yeh hamari natural beauty aur viral video ka audio preview hai."

class ScheduleRequest(BaseModel):
    platform: str = "instagram"
    scheduled_time: Optional[str] = None

@app.get("/api/ai-models")
def get_ai_models():
    return [
        {"id": k, "name": v["name"], "desc": v["desc"]}
        for k, v in SUPPORTED_AI_MODELS.items()
    ]

@app.get("/api/trends/radar")
def get_trends_radar(date_range_type: str = "last_7_days", start_date: Optional[str] = None, end_date: Optional[str] = None):
    return get_live_radar_trends(date_range_type=date_range_type, start_date=start_date, end_date=end_date)

@app.get("/api/voices")
def get_voices():
    return get_voice_list()

@app.get("/api/bgm-tracks")
def get_bgm_tracks():
    return get_bgm_list()

@app.get("/api/avatars")
def get_avatars():
    from backend.modules.avatar_engine import get_avatar_list
    return get_avatar_list()

@app.get("/api/stream/avatar/{filename}")
def stream_avatar(filename: str):
    avatar_path = os.path.join(PROJECT_ROOT, "backend", "assets", "avatars", filename)
    if os.path.exists(avatar_path):
        return FileResponse(avatar_path, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Avatar image not found")

@app.post("/api/test-voice")
def test_voice(req: TestVoiceRequest):
    try:
        temp_audio = os.path.join(PROJECT_ROOT, "storage", "audio", f"preview_{req.voice_key}.mp3")
        # Ensure Urdu voices receive 100% pure Urdu script so they pronounce cleanly
        if any(k in req.voice_key for k in ["uzma", "asad", "google_urdu", "gul", "salman", "swara", "madhur"]):
            sample = "اگر آپ کے چہرے پر بھی ضدی داغ دھبے ہیں تو یہ قدرتی روٹین دیکھیں۔"
        else:
            sample = "Welcome! This is an audio preview for our luxury beauty and fashion reels."
            
        generate_voiceover(sample, voice_key=req.voice_key, output_path=temp_audio)
        return {"status": "success", "audio_url": f"/api/stream/audio/preview_{req.voice_key}.mp3"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stream/audio/{filename}")
def stream_audio(filename: str):
    audio_path = os.path.join(PROJECT_ROOT, "storage", "audio", filename)
    if os.path.exists(audio_path):
        return FileResponse(audio_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio file not found")

@app.get("/api/videos")
def get_videos():
    return _load_db()

@app.post("/api/upload-image")
def upload_image(req: UploadImageRequest):
    saved_path = _resolve_product_image(req.image_data)
    if not saved_path:
        raise HTTPException(status_code=400, detail="Failed to process or save image")
    fname = os.path.basename(saved_path)
    return {
        "status": "success",
        "image_path": saved_path,
        "preview_url": f"/api/stream/image/{fname}"
    }

@app.get("/api/stream/image/{filename}")
def stream_image(filename: str):
    p = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(p):
        p = os.path.join(RAW_ASSETS_DIR, filename)
    if os.path.exists(p):
        ext = os.path.splitext(filename)[1].lower()
        mime = "image/png" if ext == ".png" else ("image/webp" if ext == ".webp" else "image/jpeg")
        return FileResponse(p, media_type=mime)
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/api/supermodels")
def get_supermodels():
    from backend.modules.supermodel_engine import get_supermodels_list
    return get_supermodels_list()

@app.get("/api/stream/rehearsal/{filename}")
def stream_rehearsal(filename: str):
    p = os.path.join(STORAGE_DIR, "supermodel_rehearsals", filename)
    if os.path.exists(p):
        ext = os.path.splitext(filename)[1].lower()
        mime = "video/mp4" if ext == ".mp4" else "image/jpeg"
        return FileResponse(p, media_type=mime)
    raise HTTPException(status_code=404, detail="Rehearsal asset not found")

@app.post("/api/generate-script")
def api_generate_script(req: ScriptGenerateRequest):
    try:
        from backend.modules.roman_urdu_script import generate_roman_urdu_script
        res = generate_roman_urdu_script(
            product_name=req.product_prompt,
            category=req.category,
            target_gender=req.target_gender,
            tone=req.tone,
            target_duration=req.target_duration
        )
        return {"status": "success", "script": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preview-script-audio")
def api_preview_script_audio(req: PreviewScriptAudioRequest):
    try:
        filename = f"preview_script_{uuid.uuid4().hex[:6]}.mp3"
        out_path = os.path.join(PROJECT_ROOT, "storage", "audio", filename)
        generate_voiceover(req.text, voice_key=req.voice_key, output_path=out_path)
        return {"status": "success", "audio_url": f"/api/stream/audio/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-ai-video")
def api_generate_ai_video(req: AIVideoRequest):
    try:
        from backend.modules.ai_video_generator import generate_ai_video
        res = generate_ai_video(
            prompt=req.prompt,
            image_path=req.image_path,
            provider=req.provider,
            model=req.model,
            api_key=req.api_key,
            duration=req.duration,
            aspect_ratio=req.aspect_ratio
        )
        if res.get("status") == "error":
            raise HTTPException(status_code=400, detail=res.get("message"))
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
def create_video(req: GenerateRequest):
    try:
        resolved_img = _resolve_product_image(req.product_image_data)
        record = run_pipeline(
            product_prompt=req.product_prompt,
            category=req.category,
            target_gender=req.target_gender,
            language=req.language,
            action_type=req.action_type,
            voice_key=req.voice_key,
            target_duration=req.target_duration,
            ai_model=req.ai_model,
            custom_api_key=req.api_key,
            date_range_type=req.date_range_type,
            start_date=req.start_date,
            end_date=req.end_date,
            product_image_path=resolved_img,
            bgm_track=req.bgm_track,
            avatar_character=req.avatar_character,
            avatar_layout=req.avatar_layout,
            heygen_api_key=req.heygen_api_key,
            custom_script=req.custom_script,
            supermodel_id=req.supermodel_id,
            hairstyle=req.hairstyle,
            wardrobe=req.wardrobe,
            video_engine_provider=req.video_engine_provider,
            video_engine_model=req.video_engine_model,
            video_engine_key=req.video_engine_key
        )
        return {"status": "success", "data": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/approve/{item_id}")
def approve_video(item_id: str):
    db = _load_db()
    found = False
    for item in db:
        if item["id"] == item_id:
            item["status"] = "Approved"
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Item not found")
    _save_db(db)
    return {"status": "success", "message": f"Item {item_id} approved for multi-platform publishing!"}

@app.post("/api/schedule/{item_id}")
def schedule_video(item_id: str, req: ScheduleRequest):
    import time
    db = _load_db()
    found = False
    for item in db:
        if item["id"] == item_id:
            item["status"] = "Scheduled"
            item["scheduled_platform"] = req.platform
            item["scheduled_time"] = req.scheduled_time or time.strftime("%Y-%m-%d %H:%M:%S")
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Item not found")
    _save_db(db)
    return {"status": "success", "message": f"Item {item_id} scheduled for {req.platform}!"}

@app.delete("/api/videos/{item_id}")
def delete_video(item_id: str):
    db = _load_db()
    target_idx = None
    for idx, item in enumerate(db):
        if item.get("id") == item_id:
            target_idx = idx
            break
            
    if target_idx is None:
        raise HTTPException(status_code=404, detail="Video record not found")
        
    item = db.pop(target_idx)
    
    # Remove physical video, audio, and zip pack files
    for path_key in ["video_path", "audio_path", "pack_path"]:
        p = item.get(path_key)
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except Exception as e:
                print(f"Warning: could not delete {p}: {e}")
                
    # Fallback cleanup in standard directories by item_id
    for folder, prefix, ext in [
        ("output_videos", "", ".mp4"),
        ("audio", "", ".mp3"),
        ("export_packs", "pack_", ".zip")
    ]:
        fallback_file = os.path.join(PROJECT_ROOT, "storage", folder, f"{prefix}{item_id}{ext}")
        if os.path.exists(fallback_file):
            try:
                os.remove(fallback_file)
            except Exception:
                pass
                
    _save_db(db)
    return {"status": "success", "message": f"Video {item_id} deleted successfully"}

@app.get("/api/stream/video/{filename}")
def stream_video(filename: str):
    video_path = os.path.join(PROJECT_ROOT, "storage", "output_videos", filename)
    if os.path.exists(video_path):
        return FileResponse(video_path, media_type="video/mp4")
    raise HTTPException(status_code=404, detail="Video file not found")

@app.get("/api/download/pack/{filename}")
def download_pack(filename: str):
    pack_path = os.path.join(PROJECT_ROOT, "storage", "export_packs", filename)
    if os.path.exists(pack_path):
        return FileResponse(pack_path, media_type="application/zip", filename=filename)
    raise HTTPException(status_code=404, detail="Export pack not found")

@app.get("/api/stats")
def get_stats():
    db = _load_db()
    total = len(db)
    approved = sum(1 for x in db if x.get("status") == "Approved")
    pending = total - approved
    return {
        "total_generated": total,
        "approved": approved,
        "pending_review": pending,
        "platforms_connected": ["Instagram Reels", "TikTok", "YouTube Shorts", "Facebook Reels"]
    }

# Mount static frontend
frontend_dir = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, reload=True)
