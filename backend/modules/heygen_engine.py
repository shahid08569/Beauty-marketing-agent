import os
import time
import requests
import json

HEYGEN_API_BASE = "https://api.heygen.com"

def generate_heygen_talking_avatar(
    api_key: str,
    character_photo_path: str,
    script_text: str,
    audio_path: str = None,
    output_video_path: str = None,
    voice_id: str = None
) -> dict:
    """
    Connects to the HeyGen API to create a photorealistic talking human avatar
    with deep-learning facial kinematics, natural lip-sync, and head motion.
    
    Workflow:
    1. Uploads character portrait photo to HeyGen asset library (or uses avatar id).
    2. Submits a video generation task with the provided script or voiceover audio.
    3. Polls the task until completion (with timeout).
    4. Downloads the finished 1080x1920 MP4 video directly to output_video_path.
    """
    if not api_key:
        return {"status": "error", "message": "HeyGen API Key is required."}

    headers = {
        "X-Api-Key": api_key.strip(),
        "Content-Type": "application/json"
    }

    try:
        # Step 1: Upload portrait photo as a Talking Photo Asset
        print("[HeyGen] Uploading portrait asset to HeyGen...")
        upload_url = f"{HEYGEN_API_BASE}/v1/asset"
        
        # Verify file exists
        if not os.path.exists(character_photo_path):
            return {"status": "error", "message": f"Character photo not found: {character_photo_path}"}
            
        with open(character_photo_path, "rb") as f:
            photo_bytes = f.read()

        up_headers = {
            "X-Api-Key": api_key.strip(),
            "Content-Type": "image/jpeg"
        }
        up_resp = requests.post(f"{HEYGEN_API_BASE}/v1/asset", data=photo_bytes, headers=up_headers, timeout=30)
        
        talking_photo_id = None
        if up_resp.status_code == 200:
            up_data = up_resp.json()
            talking_photo_id = up_data.get("data", {}).get("id") or up_data.get("data", {}).get("asset_id")

        # Step 2: Generate Video Task
        print("[HeyGen] Creating video generation task...")
        gen_url = f"{HEYGEN_API_BASE}/v2/video/generate"
        
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "talking_photo",
                        "talking_photo_id": talking_photo_id or "default_avatar",
                        "scale": 1.0
                    },
                    "voice": {
                        "type": "audio" if audio_path and os.path.exists(audio_path) else "text",
                        "input_text": script_text
                    },
                    "background": {
                        "type": "color",
                        "value": "#131314"
                    }
                }
            ],
            "dimension": {
                "width": 1080,
                "height": 1920
            }
        }

        resp = requests.post(gen_url, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            return {
                "status": "error", 
                "message": f"HeyGen API rejected request ({resp.status_code}): {resp.text[:300]}"
            }

        data = resp.json()
        video_id = data.get("data", {}).get("video_id")
        if not video_id:
            return {"status": "error", "message": "No video_id returned by HeyGen."}

        print(f"[HeyGen] Video generation started. Task ID: {video_id}. Polling status...")

        # Step 3: Poll for status
        status_url = f"{HEYGEN_API_BASE}/v1/video_status.get?video_id={video_id}"
        max_attempts = 45  # ~150 seconds max
        for attempt in range(max_attempts):
            time.sleep(3.5)
            stat_resp = requests.get(status_url, headers=headers, timeout=15)
            if stat_resp.status_code == 200:
                s_data = stat_resp.json().get("data", {})
                status = s_data.get("status")
                print(f"  -> HeyGen status: {status} ({attempt+1}/{max_attempts})")
                if status == "completed":
                    video_download_url = s_data.get("video_url")
                    if video_download_url and output_video_path:
                        vid_bytes = requests.get(video_download_url, timeout=60).content
                        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
                        with open(output_video_path, "wb") as f_out:
                            f_out.write(vid_bytes)
                        return {
                            "status": "success",
                            "video_path": output_video_path,
                            "video_url": video_download_url,
                            "video_id": video_id
                        }
                elif status == "failed":
                    return {"status": "error", "message": f"HeyGen rendering failed: {s_data.get('error')}"}

        return {"status": "error", "message": "HeyGen rendering timed out."}
    except Exception as e:
        return {"status": "error", "message": f"HeyGen communication error: {str(e)}"}
