import os
import subprocess
import shutil
import json
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage")
REHEARSAL_DIR = os.path.join(STORAGE_DIR, "supermodel_rehearsals")

def find_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if path:
        return path
    custom_path = r"C:\Users\Shahid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
    if os.path.exists(custom_path):
        return custom_path
    return "ffmpeg"

SUPERMODELS = {
    "ayesha_derm": {
        "id": "ayesha_derm",
        "name": "Dr. Ayesha Khan",
        "role": "Senior Consultant Dermatologist",
        "category": "Clinical & Medical Skincare",
        "badge": "MBBS, FCPS Verified",
        "desc": "Radiant skincare expert in luxury modern studio demonstrating authentic product with rich lather and glowing skin.",
        "hair_presets": ["Professional Low Bun", "Elegant Blowdry Waves", "Clinical Headscarf"],
        "wardrobe_presets": ["White Clinical Lab Coat", "Formal Silk Scrubs", "Hospital Blazer"],
        "lighting_mood": "Clean Hospital Studio",
        "rehearsal_file": "ayesha_derm.mp4",
        "rehearsal_image": "ayesha_derm.jpg"
    },
    "hamza_grooming": {
        "id": "hamza_grooming",
        "name": "Hamza Qureshi (Dr. Saleem)",
        "role": "Men's Clinical Grooming & Skin Specialist",
        "category": "Men's Grooming & Clinical Care",
        "badge": "Clinical Aesthetic Pro",
        "desc": "Sharp, charismatic male aesthetician in lab coat, crisp styled hair, professional bedside manner.",
        "hair_presets": ["Textured High Fade", "Classic Side Part", "Natural Waves"],
        "wardrobe_presets": ["White Doctor Coat & Black Shirt", "Charcoal Tailored Suit", "Minimalist Black Scrubs"],
        "lighting_mood": "Modern Clinical Suite",
        "rehearsal_file": "hamza_grooming.mp4",
        "rehearsal_image": "hamza_grooming.jpg"
    },
    "zoya_glamour": {
        "id": "zoya_glamour",
        "name": "Zoya Malik",
        "role": "High-Fashion Glamour & Beauty Creator",
        "category": "Luxury Skincare & Glamour",
        "badge": "Top Beauty Supermodel",
        "desc": "Youthful, radiant luxury supermodel with flowing silky hair, expressive smiling eyes, and captivating presence.",
        "hair_presets": ["Sleek Glossy Waves", "Voluminous 90s Blowout", "Half-Up Glamour Pony"],
        "wardrobe_presets": ["Minimalist Silk Shirt", "Pastel Studio Linen", "Velvet Evening Gown"],
        "lighting_mood": "Warm Vanity Glow",
        "rehearsal_file": "zoya_glamour.mp4",
        "rehearsal_image": "zoya_glamour.jpg"
    },
    "aaliyah_runway": {
        "id": "aaliyah_runway",
        "name": "Aaliyah Noor",
        "role": "Editorial Runway & Streetstyle Model",
        "category": "High Fashion & Lifestyle",
        "badge": "Runway Supermodel",
        "desc": "Striking features, confident walking camera shots, traditional elegance with modern high-fashion poise.",
        "hair_presets": ["Royal Traditional Braids", "High Runway Ponytail", "Open Center-Parted Silk"],
        "wardrobe_presets": ["Modern Embroidered Kurta", "Raw Silk Trench", "Minimalist High-Fashion Tunic"],
        "lighting_mood": "Natural Outdoor Sunlight",
        "rehearsal_file": "aaliyah_runway.mp4",
        "rehearsal_image": "aaliyah_runway.jpg"
    },
    "zara_aesthetic": {
        "id": "zara_aesthetic",
        "name": "Zara Farooq",
        "role": "Botanical & Clean Organic Advisor",
        "category": "Clean Beauty & Natural Care",
        "badge": "Organic Certified",
        "desc": "Calm, studious, gentle aesthetic focusing on gentle botanical care, soothing tones, and relatable honesty.",
        "hair_presets": ["Natural Soft Curls", "Simple Loose Plait", "Minimalist Claw Clip"],
        "wardrobe_presets": ["Earthy Cotton Shalwar", "Oatmeal Knit Cardigan", "Sage Green Botanical Tunic"],
        "lighting_mood": "Soft Daylight & Indoor Greenery",
        "rehearsal_file": "zara_aesthetic.mp4",
        "rehearsal_image": "zara_aesthetic.jpg"
    },
    "bibi_heritage": {
        "id": "bibi_heritage",
        "name": "Bibi Gul",
        "role": "Traditional Desi Heritage Storyteller",
        "category": "Cultural & Emotional Storytelling",
        "badge": "Heritage Wisdom",
        "desc": "Emotional, beloved matriarch with genuine maternal warmth, rustic courtyard setting, and authentic blessings.",
        "hair_presets": ["Traditional Grey Dupatta", "Embroidered Chador"],
        "wardrobe_presets": ["Handwoven Grey Cotton Suit", "Traditional Khaddar Kameez"],
        "lighting_mood": "Rustic Courtyard Sunlight",
        "rehearsal_file": "bibi_heritage.mp4",
        "rehearsal_image": "bibi_heritage.jpg"
    }
}

def get_supermodels_list():
    result = []
    for k, v in SUPERMODELS.items():
        m = v.copy()
        m["rehearsal_video"] = f"/api/stream/rehearsal/{v['rehearsal_file']}"
        m["rehearsal_image"] = f"/api/stream/rehearsal/{v['rehearsal_image']}"
        result.append(m)
    return result

def render_supermodel_cinematic_reel(
    supermodel_id: str,
    audio_path: str,
    output_video_path: str,
    product_name: str,
    hook_text: str,
    product_image_path: str = None,
    hairstyle: str = "Natural",
    wardrobe: str = "Standard",
    target_duration: int = 30,
    source_video_override: str = None
) -> str:
    """
    Renders a full-bleed 1080x1920 vertical cinematic reel using the selected 3D supermodel footage.
    Includes:
    - High-definition full-bleed motion loop
    - Top model verification badge
    - Clean bottom lower-third banner with model title, chosen hairstyle/wardrobe, and Roman Urdu hook
    - Side product showcase card if product image is provided
    - Synchronized Roman Urdu voiceover audio
    """
    ffmpeg_bin = find_ffmpeg()
    model = SUPERMODELS.get(supermodel_id, SUPERMODELS["ayesha_derm"])
    source_clip = os.path.join(REHEARSAL_DIR, model["rehearsal_file"])
    dove_multi = os.path.join(PROJECT_ROOT, "storage", "output_videos", "dove_soap_official_commercial.mp4")
    
    if source_video_override and os.path.exists(source_video_override):
        source_clip = source_video_override
    elif "dove" in product_name.lower() and os.path.exists(dove_multi):
        source_clip = dove_multi
    elif not os.path.exists(source_clip):
        source_clip = os.path.join(REHEARSAL_DIR, "ayesha_derm.mp4")

    # Get audio duration
    try:
        p = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ], capture_output=True, text=True)
        dur = float(p.stdout.strip())
        dur = max(10.0, min(60.0, dur + 1.0))
    except Exception:
        dur = float(target_duration)

    width, height = 1080, 1920
    temp_dir = os.path.dirname(output_video_path) or "."
    overlay_path = os.path.join(temp_dir, f"sm_overlay_{os.path.basename(output_video_path)}.png")

    FONT_DIR = r"C:\Windows\Fonts"
    try:
        font_pill = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 22)
        font_title = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 40)
        font_sub = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 24)
        font_cta = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 22)
    except Exception:
        font_pill = font_title = font_sub = font_cta = ImageFont.load_default()

    # 1. Build Branded Lower Third and Cinematic Overlays
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Top Model Pill
    d.rounded_rectangle([(40, 50), (width - 40, 115)], radius=26, fill=(15, 17, 23, 220), outline=(255, 255, 255, 90), width=1)
    d.ellipse([(65, 73), (85, 93)], fill=(16, 185, 129, 255))
    d.text((105, 68), f"3D AI MODEL • {model['name'].upper()} • {model['badge'].upper()}", font=font_pill, fill=(247, 245, 240, 255))

    # Bottom Cinematic Card
    by = 1350
    bh = 500
    d.rounded_rectangle([(40, by), (width - 40, by + bh)], radius=36, fill=(12, 14, 18, 235), outline=(255, 255, 255, 80), width=1)

    d.text((75, by + 40), model["name"], font=font_title, fill=(247, 245, 240, 255))
    d.text((75, by + 98), f"{model['role']} • Style: {hairstyle} • Look: {wardrobe}", font=font_sub, fill=(16, 185, 129, 255))
    d.line([(75, by + 145), (width - 75, by + 145)], fill=(255, 255, 255, 40), width=1)

    clean_hook = (hook_text or "").strip()
    if not clean_hook:
        clean_hook = f"Experience authentic results with {product_name}."

    if len(clean_hook) > 55:
        mid = clean_hook.rfind(" ", 0, 50)
        if mid == -1: mid = 45
        d.text((75, by + 175), f'"{clean_hook[:mid]}"', font=font_title, fill=(255, 255, 255, 255))
        d.text((75, by + 230), f'"{clean_hook[mid:].strip()}"', font=font_title, fill=(255, 255, 255, 255))
    else:
        d.text((75, by + 185), f'"{clean_hook}"', font=font_title, fill=(255, 255, 255, 255))

    d.text((75, by + 315), f"Product: {product_name} • 100% Verified Authentic Batch", font=font_sub, fill=(209, 213, 219, 255))

    # COD Verification Pill
    d.rounded_rectangle([(75, by + 380), (width - 75, by + 465)], radius=20, fill=(16, 185, 129, 235))
    d.text((120, by + 408), "● VERIFIED ORIGINAL STOCK • CASH ON DELIVERY PK", font=font_cta, fill=(255, 255, 255, 255))

    # If product image provided, composite product card into overlay
    if product_image_path and os.path.exists(product_image_path):
        try:
            prod_img = Image.open(product_image_path).convert("RGBA")
            # Create a 240x240 floating product card in upper right
            px, py, ps = width - 290, 160, 240
            d.rounded_rectangle([(px - 4, py - 4), (px + ps + 4, py + ps + 4)], radius=28, fill=(255, 255, 255, 240), outline=(220, 38, 38, 200), width=2)
            prod_img.thumbnail((ps - 20, ps - 20), Image.Resampling.LANCZOS)
            offset_x = px + (ps - prod_img.width) // 2
            offset_y = py + (ps - prod_img.height) // 2
            overlay.paste(prod_img, (offset_x, offset_y), prod_img)
            d.rounded_rectangle([(px, py + ps - 30), (px + ps, py + ps + 8)], radius=12, fill=(15, 17, 23, 240))
            d.text((px + 20, py + ps - 22), "AUTHENTIC PRODUCT", font=font_pill, fill=(16, 185, 129, 255))
        except Exception as e:
            print(f"[SupermodelEngine] Product overlay error: {e}")

    overlay.save(overlay_path, "PNG")

    # 2. FFmpeg Command: Loop model footage to match audio duration, scale to 1080x1920, overlay UI, encode H.264
    cmd = [
        ffmpeg_bin, "-y",
        "-stream_loop", "-1",
        "-i", source_clip,
        "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex", (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30[bg];"
            f"[bg][1:v]overlay=0:0[vout]"
        ),
        "-map", "[vout]",
        "-map", "2:a",
        "-t", str(dur),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_video_path
    ]

    print(f"[SupermodelEngine] Rendering 1080x1920 cinematic reel for {model['name']} ({dur}s)...")
    res = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(overlay_path):
        try: os.remove(overlay_path)
        except Exception: pass

    if res.returncode != 0:
        raise RuntimeError(f"Supermodel reel render failed: {res.stderr[-300:]}")

    print(f"[SupermodelEngine] SUCCESS: Rendered {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
    return output_video_path
