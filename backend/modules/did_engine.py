import os
import time
import json
import base64
import subprocess
import shutil
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont

def find_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if path:
        return path
    custom_path = r"C:\Users\Shahid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
    if os.path.exists(custom_path):
        return custom_path
    return "ffmpeg"

def format_talking_avatar_reel(
    input_video: str,
    output_video: str,
    avatar_name: str = "Dr. Ayesha Khan",
    avatar_role: str = "Senior Clinical Dermatologist",
    product_name: str = "Dove",
    hook_text: str = "Stubborn spots, open pores, and dull complexion?",
    width: int = 1080,
    height: int = 1920
):
    """
    Composites a square 512x512 talking face video into a full-bleed 1080x1920 vertical commercial reel.
    Includes:
    - High-def blurred background
    - Crisp center presenter window with studio border
    - Top presenter credential pill
    - Modern lower third card with title, role, hook & product focus
    - Cash on Delivery verification badge
    """
    ffmpeg_bin = find_ffmpeg()
    temp_dir = os.path.dirname(output_video) or "."
    overlay_path = os.path.join(temp_dir, f"did_overlay_{os.path.basename(output_video)}.png")

    FONT_DIR = r"C:\Windows\Fonts"
    try:
        font_pill = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 22)
        font_title = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 38)
        font_sub = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 23)
        font_cta = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 22)
    except Exception:
        font_pill = font_title = font_sub = font_cta = ImageFont.load_default()

    # 1. Branded transparent UI overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Top Broadcaster Pill
    d.rounded_rectangle([(40, 50), (width - 40, 115)], radius=26, fill=(19, 19, 20, 220), outline=(255, 255, 255, 90), width=1)
    d.ellipse([(65, 73), (85, 93)], fill=(16, 185, 129, 255))
    d.text((100, 68), f"AI TALKING HERO • {avatar_name.upper()} • VERIFIED", font=font_pill, fill=(247, 245, 240, 255))

    # Face Frame Border
    fx, fy, fw, fh = (width - 820) // 2, 220, 820, 820
    d.rounded_rectangle([(fx - 6, fy - 6), (fx + fw + 6, fy + fh + 6)], radius=28, outline=(255, 255, 255, 120), width=3)

    # Lower Third Branded Card
    by = 1200
    bh = 650
    d.rounded_rectangle([(40, by), (width - 40, by + bh)], radius=36, fill=(15, 15, 18, 235), outline=(255, 255, 255, 90), width=1)

    d.text((75, by + 45), avatar_name, font=font_title, fill=(247, 245, 240, 255))
    d.text((75, by + 105), f"{avatar_role} • Live AI Voice Performance", font=font_sub, fill=(16, 185, 129, 255))
    d.line([(75, by + 155), (width - 75, by + 155)], fill=(255, 255, 255, 40), width=1)

    clean_hook = (hook_text or "").strip()
    if not clean_hook:
        clean_hook = f"Experience clinical results with {product_name}."
    
    if len(clean_hook) > 60:
        mid = clean_hook.rfind(" ", 0, 50)
        if mid == -1: mid = 45
        d.text((75, by + 185), f'"{clean_hook[:mid]}"', font=font_title, fill=(255, 255, 255, 255))
        d.text((75, by + 240), f'"{clean_hook[mid:].strip()}"', font=font_title, fill=(255, 255, 255, 255))
    else:
        d.text((75, by + 195), f'"{clean_hook}"', font=font_title, fill=(255, 255, 255, 255))

    d.text((75, by + 340), f"Product Focus: {product_name} • Authentic Cellular Glow Routine", font=font_sub, fill=(209, 213, 219, 255))

    # COD Verification Pill
    d.rounded_rectangle([(75, by + 450), (width - 75, by + 545)], radius=22, fill=(16, 185, 129, 235))
    d.text((120, by + 480), "● 100% VERIFIED AUTHENTIC BATCH • CASH ON DELIVERY PK", font=font_cta, fill=(255, 255, 255, 255))

    overlay.save(overlay_path, "PNG")

    # 2. FFmpeg composite
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        f"[0:v]scale={fw}:{fh}[fg];"
        f"[bg][fg]overlay={fx}:{fy}[vcomp];"
        "[vcomp][1:v]overlay=0:0[vout]"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-i", input_video,
        "-i", overlay_path,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_video
    ]

    print("[D-ID] Formatting talking avatar into 1080x1920 vertical commercial reel...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(overlay_path):
        try: os.remove(overlay_path)
        except Exception: pass

    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg composite failed: {res.stderr[-300:]}")
    print(f"[D-ID] Successfully rendered 1080x1920 reel: {output_video} ({os.path.getsize(output_video)} bytes)")

def generate_did_talking_avatar(
    api_key: str,
    character_photo_path: str,
    script_text: str,
    voice_key: str = "ur-PK-UzmaNeural",
    audio_path: str = None,
    output_video_path: str = None,
    avatar_character: str = "ayesha_derm",
    product_name: str = "Dove",
    hook_text: str = ""
) -> dict:
    """
    Calls D-ID API (https://api.d-id.com/talks) to create an AI Talking Avatar.
    Supports both free trial API keys (Basic Auth) and custom voice/text inputs.
    Automatically wraps the square 512x512 output into a vertical 1080x1920 commercial reel.
    """
    if not api_key:
        api_key = os.environ.get("DID_API_KEY")
    if not api_key:
        return {"status": "error", "message": "D-ID API key is missing"}

    # Format authorization header
    if ":" in api_key:
        auth_str = base64.b64encode(api_key.encode()).decode()
    else:
        auth_str = base64.b64encode(f"{api_key}:".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_str}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    # 1. Upload source image to D-ID
    image_url = None
    try:
        with open(character_photo_path, "rb") as f:
            img_bytes = f.read()
            
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="{os.path.basename(character_photo_path)}"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode("utf-8") + img_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

        upload_req = urllib.request.Request(
            "https://api.d-id.com/images",
            data=body,
            headers={
                "Authorization": f"Basic {auth_str}",
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            }
        )
        with urllib.request.urlopen(upload_req, timeout=30) as r:
            upload_res = json.loads(r.read().decode())
            image_url = upload_res.get("url")
            print(f"[D-ID] Uploaded image url: {image_url}")
    except Exception as e:
        print(f"[D-ID] Image upload fallback: {e}")
        image_url = "https://raw.githubusercontent.com/OpenTalker/SadTalker/main/examples/source_image/art_10.png"

    # 2. Prepare payload
    ms_voice = "ur-PK-UzmaNeural" if "uzma" in str(voice_key).lower() or "female" in str(voice_key).lower() else "ur-PK-AsadNeural"
    
    payload = {
        "source_url": image_url,
        "script": {
            "type": "text",
            "subtitles": "false",
            "provider": {
                "type": "microsoft",
                "voice_id": ms_voice
            },
            "input": script_text[:800]
        },
        "config": {
            "fluent": "true",
            "pad_audio": "0.0"
        }
    }

    # 3. Submit talk task
    try:
        req = urllib.request.Request(
            "https://api.d-id.com/talks",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            talk_res = json.loads(r.read().decode())
            talk_id = talk_res.get("id")
            print(f"[D-ID] Talk task submitted, ID: {talk_id}")

        if not talk_id:
            return {"status": "error", "message": "Failed to obtain talk ID from D-ID"}

        # 4. Poll task status
        poll_url = f"https://api.d-id.com/talks/{talk_id}"
        poll_req = urllib.request.Request(poll_url, headers=headers)
        
        for attempt in range(40):
            time.sleep(3.5)
            with urllib.request.urlopen(poll_req, timeout=20) as r:
                status_res = json.loads(r.read().decode())
                task_status = status_res.get("status")
                print(f"[D-ID] Poll {attempt+1}: Status = {task_status}")
                if task_status == "done":
                    result_video_url = status_res.get("result_url")
                    if result_video_url and output_video_path:
                        raw_temp_path = output_video_path.replace(".mp4", "_raw512.mp4")
                        print(f"[D-ID] Downloading raw talking video: {result_video_url}")
                        urllib.request.urlretrieve(result_video_url, raw_temp_path)
                        
                        # Look up avatar metadata
                        from backend.modules.avatar_engine import AVATAR_PRESETS
                        preset = AVATAR_PRESETS.get(avatar_character, {})
                        av_name = preset.get("name", "Dr. Ayesha Khan")
                        av_title = preset.get("title", "Clinical Consultant")
                        
                        try:
                            format_talking_avatar_reel(
                                input_video=raw_temp_path,
                                output_video=output_video_path,
                                avatar_name=av_name,
                                avatar_role=av_title,
                                product_name=product_name,
                                hook_text=hook_text
                            )
                            if os.path.exists(raw_temp_path):
                                try: os.remove(raw_temp_path)
                                except Exception: pass
                        except Exception as fe:
                            print(f"[D-ID] Reel formatting warning: {fe}, keeping raw download.")
                            if os.path.exists(raw_temp_path):
                                if os.path.exists(output_video_path):
                                    os.remove(output_video_path)
                                os.rename(raw_temp_path, output_video_path)

                        return {
                            "status": "success",
                            "video_path": output_video_path,
                            "video_url": result_video_url
                        }
                    return {"status": "success", "video_url": result_video_url}
                elif task_status == "error":
                    return {"status": "error", "message": status_res.get("error", "D-ID generation error")}

        return {"status": "error", "message": "D-ID task timed out"}

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        return {"status": "error", "message": f"D-ID API HTTP {e.code}: {err_msg}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
