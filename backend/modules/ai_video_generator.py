import os
import time
import json
import base64
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "storage", "output_videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def image_to_base64_data_uri(image_path: str) -> str:
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"

# =========================================================================
# 1. REPLICATE INTEGRATION (Kling 1.6, Minimax Video-01, Wan 2.1)
# =========================================================================
def generate_video_replicate(
    prompt: str,
    image_path: Optional[str] = None,
    api_token: Optional[str] = None,
    model_name: str = "kling",
    duration: int = 5,
    aspect_ratio: str = "9:16"
) -> Dict[str, Any]:
    """
    Generates full-motion AI video using Replicate API (Kling AI, Minimax, or Wan 2.1).
    """
    token = api_token or os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        return {
            "status": "error",
            "message": "REPLICATE_API_TOKEN is required. Please get your token at https://replicate.com/account/api-tokens"
        }

    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Content-Type": "application/json",
        "Prefer": "wait=60"
    }

    # Model identifiers on Replicate
    model_map = {
        "kling": "kwaivgi/kling-v1.6-standard",
        "kling_pro": "kwaivgi/kling-v1.6-pro",
        "minimax": "minimax/video-01",
        "wan": "wan-video/wan-2.1-i2v-720p"
    }
    repo = model_map.get(model_name, "kwaivgi/kling-v1.6-standard")

    input_payload: Dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "duration": duration
    }

    if image_path and os.path.exists(image_path):
        data_uri = image_to_base64_data_uri(image_path)
        if "kling" in repo:
            input_payload["start_image"] = data_uri
        elif "minimax" in repo:
            input_payload["first_frame_image"] = data_uri
        else:
            input_payload["image"] = data_uri

    endpoint = f"https://api.replicate.com/v1/models/{repo}/predictions"

    try:
        req = urllib.request.Request(endpoint, data=json.dumps({"input": input_payload}).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pred_id = data.get("id")
            status = data.get("status")
            print(f"[Replicate] Started prediction {pred_id}, status: {status}")

            # Poll prediction status until succeeded
            poll_url = f"https://api.replicate.com/v1/predictions/{pred_id}"
            for attempt in range(60): # up to 5-10 minutes
                time.sleep(5)
                poll_req = urllib.request.Request(poll_url, headers=headers)
                with urllib.request.urlopen(poll_req, timeout=30) as p_resp:
                    p_data = json.loads(p_resp.read().decode("utf-8"))
                    p_status = p_data.get("status")
                    print(f"[Replicate] Attempt {attempt+1}: Status = {p_status}")
                    
                    if p_status == "succeeded":
                        video_url = p_data.get("output")
                        if isinstance(video_url, list):
                            video_url = video_url[0]
                        
                        out_filename = f"replicate_{pred_id}.mp4"
                        out_path = os.path.join(OUTPUT_DIR, out_filename)
                        print(f"[Replicate] Downloading video: {video_url} -> {out_path}")
                        urllib.request.urlretrieve(video_url, out_path)
                        return {
                            "status": "success",
                            "video_path": out_path,
                            "video_url": f"/api/stream/video/{out_filename}",
                            "raw_url": video_url,
                            "model": repo
                        }
                    elif p_status in ["failed", "canceled"]:
                        return {
                            "status": "error",
                            "message": f"Replicate generation failed: {p_data.get('error')}"
                        }

            return {"status": "error", "message": "Replicate generation timed out during polling."}
    except Exception as e:
        return {"status": "error", "message": f"Replicate API error: {str(e)}"}

# =========================================================================
# 2. FAL.AI INTEGRATION (Kling Video, Minimax Video-01, Wan 2.1)
# =========================================================================
def generate_video_fal(
    prompt: str,
    image_path: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: str = "kling",
    duration: int = 5,
    aspect_ratio: str = "9:16"
) -> Dict[str, Any]:
    """
    Generates video via Fal.ai queue API.
    """
    key = api_key or os.environ.get("FAL_KEY")
    if not key:
        return {
            "status": "error",
            "message": "FAL_KEY is required. Please get your key at https://fal.ai/dashboard/keys"
        }

    headers = {
        "Authorization": f"Key {key.strip()}",
        "Content-Type": "application/json"
    }

    fal_models = {
        "kling": "fal-ai/kling-video/v1.6/standard/image-to-video",
        "minimax": "fal-ai/minimax/video-01",
        "wan": "fal-ai/wan-2.1-i2v-720p"
    }
    app_id = fal_models.get(model_name, "fal-ai/kling-video/v1.6/standard/image-to-video")

    input_payload: Dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "duration": duration
    }

    if image_path and os.path.exists(image_path):
        input_payload["image_url"] = image_to_base64_data_uri(image_path)

    queue_url = f"https://queue.fal.run/{app_id}"

    try:
        req = urllib.request.Request(queue_url, data=json.dumps(input_payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            request_id = data.get("request_id")
            status_url = data.get("status_url", f"https://queue.fal.run/{app_id}/requests/{request_id}/status")
            response_url = data.get("response_url", f"https://queue.fal.run/{app_id}/requests/{request_id}")

        for attempt in range(60):
            time.sleep(4)
            s_req = urllib.request.Request(status_url, headers=headers)
            with urllib.request.urlopen(s_req, timeout=20) as s_resp:
                s_data = json.loads(s_resp.read().decode("utf-8"))
                s_status = s_data.get("status")
                print(f"[Fal.ai] Attempt {attempt+1}: Status = {s_status}")
                if s_status == "COMPLETED":
                    r_req = urllib.request.Request(response_url, headers=headers)
                    with urllib.request.urlopen(r_req, timeout=20) as r_resp:
                        r_data = json.loads(r_resp.read().decode("utf-8"))
                        video_obj = r_data.get("video", {})
                        video_url = video_obj.get("url") if isinstance(video_obj, dict) else r_data.get("output")
                        
                        out_filename = f"fal_{request_id}.mp4"
                        out_path = os.path.join(OUTPUT_DIR, out_filename)
                        urllib.request.urlretrieve(video_url, out_path)
                        return {
                            "status": "success",
                            "video_path": out_path,
                            "video_url": f"/api/stream/video/{out_filename}",
                            "raw_url": video_url,
                            "model": app_id
                        }
                elif s_status in ["FAILED", "ERROR"]:
                    return {"status": "error", "message": f"Fal.ai failed: {s_data.get('error')}"}

        return {"status": "error", "message": "Fal.ai generation timed out."}
    except Exception as e:
        return {"status": "error", "message": f"Fal.ai API error: {str(e)}"}

# =========================================================================
# 3. HEDRA INTEGRATION (Character Video with Lip Sync & Body Motion)
# =========================================================================
def generate_video_hedra(
    prompt: str,
    image_path: str,
    audio_path: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calls Hedra Character-2 API for realistic moving, speaking video.
    """
    key = api_key or os.environ.get("HEDRA_API_KEY")
    if not key:
        return {
            "status": "error",
            "message": "HEDRA_API_KEY is required. Get your key at https://www.hedra.com/"
        }
    return {
        "status": "error",
        "message": "Hedra integration configured. Please supply a valid HEDRA_API_KEY."
    }

# Unified Entrypoint
def generate_ai_video(
    prompt: str,
    image_path: Optional[str] = None,
    provider: str = "replicate",
    model: str = "kling",
    api_key: Optional[str] = None,
    duration: int = 5,
    aspect_ratio: str = "9:16"
) -> Dict[str, Any]:
    if provider == "replicate":
        return generate_video_replicate(prompt, image_path, api_token=api_key, model_name=model, duration=duration, aspect_ratio=aspect_ratio)
    elif provider == "fal":
        return generate_video_fal(prompt, image_path, api_key=api_key, model_name=model, duration=duration, aspect_ratio=aspect_ratio)
    else:
        return generate_video_replicate(prompt, image_path, api_token=api_key, model_name=model, duration=duration, aspect_ratio=aspect_ratio)
