import os
import math
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AVATAR_DIR = os.path.join(PROJECT_ROOT, "backend", "assets", "avatars")
FONT_DIR = r"C:\Windows\Fonts"

def find_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if path:
        return path
    custom_path = r"C:\Users\Shahid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
    if os.path.exists(custom_path):
        return custom_path
    return "ffmpeg"

# 6 High-Impact, Realistic Pakistani & Desi Avatars
AVATAR_PRESETS = {
    "ayesha_derm": {
        "id": "ayesha_derm",
        "name": "Dr. Ayesha Khan",
        "title": "Senior Consultant Dermatologist",
        "credentials": "MBBS, FCPS (Dermatology)",
        "gender": "female",
        "recommended_voice": "uzma_pk",
        "style_category": "Clinical & Evidence-Backed",
        "accent_color": "#0D9488",  # Medical teal
        "badge": "Dermatologist Verified",
        "desc": "Authoritative clinical perspective. Ideal for active serums, acne solutions, retinol, and medical dermocosmetics."
    },
    "uzma_creator": {
        "id": "uzma_creator",
        "name": "Uzma Siddiqui",
        "title": "Skincare & Beauty Creator",
        "credentials": "Beauty Creator • 450K+ Community",
        "gender": "female",
        "recommended_voice": "uzma_pk",
        "style_category": "Lifestyle & Daily Glow",
        "accent_color": "#EC4899",  # Soft rose pink
        "badge": "Top Skincare Creator",
        "desc": "Aesthetic, radiant, conversational. Ideal for daily face wash, moisturizers, glow kits, and trending routines."
    },
    "asad_grooming": {
        "id": "asad_grooming",
        "name": "Asad Malik",
        "title": "Men's Grooming Specialist",
        "credentials": "Men's Care & Beard Expert",
        "gender": "male",
        "recommended_voice": "asad_pk",
        "style_category": "Men's Grooming & Precision",
        "accent_color": "#4F46E5",  # Sharp indigo
        "badge": "Grooming Specialist",
        "desc": "Sharp, confident, straightforward. Ideal for men's charcoal cleansers, beard growth oils, and anti-pollution formulas."
    },
    "zara_herbal": {
        "id": "zara_herbal",
        "name": "Zara Noor",
        "title": "Herbal & Organic Skincare Advisor",
        "credentials": "Certified Botanical Aesthetician",
        "gender": "female",
        "recommended_voice": "uzma_pk",
        "style_category": "Organic & Clean Beauty",
        "accent_color": "#16A34A",  # Emerald green
        "badge": "Organic Certified",
        "desc": "Gentle, nature-focused, soothing. Ideal for aloe vera, neem, tea tree, rose water, and organic skincare formulations."
    },
    "bilal_fitness": {
        "id": "bilal_fitness",
        "name": "Bilal Ahmed",
        "title": "Active Life & Grooming Creator",
        "credentials": "Fitness & Lifestyle Creator",
        "gender": "male",
        "recommended_voice": "asad_pk",
        "style_category": "Active Sports & Energy",
        "accent_color": "#EA580C",  # Vibrant energizing orange
        "badge": "Active Care Pro",
        "desc": "High energy, fast-paced, active routine. Ideal for sweat-proof sunscreen, sport body wash, and oil-control face washes."
    },
    "tariq_cosmo": {
        "id": "tariq_cosmo",
        "name": "Dr. Farhan Tariq",
        "title": "Aesthetic Cosmetologist & Formula Specialist",
        "credentials": "Chief Aesthetic Cosmetologist",
        "gender": "male",
        "recommended_voice": "salman_in",
        "style_category": "Anti-Aging & Formula Science",
        "accent_color": "#2563EB",  # Deep medical royal
        "badge": "Formula Scientist",
        "desc": "Experienced, sophisticated, deep scientific authority. Ideal for anti-aging creams, multi-peptide serums, and chemical peels."
    }
}

def get_avatar_list() -> list:
    """Returns a list of all 6 avatars with their full profile and photo availability status."""
    result = []
    for aid, data in AVATAR_PRESETS.items():
        img_path = get_avatar_image_path(aid)
        item = dict(data)
        item["has_photo"] = os.path.exists(img_path)
        item["photo_url"] = f"/api/stream/avatar/{aid}.jpg"
        result.append(item)
    return result

def get_avatar_image_path(avatar_id: str) -> str:
    """Returns path to the avatar portrait image (jpg or png)."""
    jpg_path = os.path.join(AVATAR_DIR, f"{avatar_id}.jpg")
    if os.path.exists(jpg_path):
        return jpg_path
    png_path = os.path.join(AVATAR_DIR, f"{avatar_id}.png")
    if os.path.exists(png_path):
        return png_path
    return jpg_path

def generate_pip_talking_loop(
    avatar_id: str,
    output_mov_path: str,
    size: int = 340,
    fps: int = 20,
    loop_duration: float = 2.0
) -> str:
    """
    Renders an animated 2-second QuickTime Animation (qtrle) loop with alpha channel
    incorporating:
    - Organic speech mouth articulation (at ~3.2 Hz natural Urdu phoneme tempo)
    - Natural subtle chest/camera breathing sway (sinusoidal scaling)
    - High-visibility pulsating green 'LIVE' indicator
    - Polished double-ring luxury metallic border & drop shadow
    - Presenter nameplate ribbon
    """
    os.makedirs(os.path.dirname(output_mov_path), exist_ok=True)
    temp_dir = os.path.join(os.path.dirname(output_mov_path), f"tmp_loop_{avatar_id}")
    os.makedirs(temp_dir, exist_ok=True)

    img_p = get_avatar_image_path(avatar_id)
    preset = AVATAR_PRESETS.get(avatar_id, AVATAR_PRESETS["uzma_creator"])

    if os.path.exists(img_p):
        raw_img = Image.open(img_p).convert("RGBA")
    else:
        raw_img = Image.new("RGBA", (size, size), (247, 245, 240, 255))

    # Center crop square with slight upward bias to focus on face
    w, h = raw_img.size
    min_d = min(w, h)
    top_offset = int((h - min_d) * 0.12)
    left_offset = (w - min_d) // 2
    cropped = raw_img.crop((left_offset, top_offset, left_offset + min_d, top_offset + min_d)).resize((size, size), Image.Resampling.LANCZOS)

    # Prepare resting frame and speaking frame with jaw articulation
    rest_frame = cropped.copy()
    speak_frame = cropped.copy()
    jaw_box = (int(size * 0.35), int(size * 0.60), int(size * 0.65), int(size * 0.85))
    jaw_crop = cropped.crop(jaw_box)
    speak_frame.paste(jaw_crop, (jaw_box[0], jaw_box[1] + 3))

    # High-quality anti-aliased circular mask
    scale = 3
    mask_lg = Image.new("L", (size * scale, size * scale), 0)
    ImageDraw.Draw(mask_lg).ellipse((0, 0, size * scale, size * scale), fill=255)
    mask = mask_lg.resize((size, size), Image.Resampling.LANCZOS)

    # Fonts
    try:
        font_sm = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 10)
        font_name = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 11)
    except Exception:
        font_sm = ImageFont.load_default()
        font_name = ImageFont.load_default()

    num_frames = int(loop_duration * fps)
    for f in range(num_frames):
        t = f / fps
        is_speaking = (math.sin(2 * math.pi * 3.2 * t) > 0.0)
        base = speak_frame if is_speaking else rest_frame

        # Natural breathing sway
        b_scale = 1.0 + 0.015 * math.sin(2 * math.pi * t / loop_duration)
        sw = int(size * b_scale)
        sh = int(size * b_scale)
        resized = base.resize((sw, sh), Image.Resampling.BILINEAR)
        off_x = (sw - size) // 2
        off_y = (sh - size) // 2
        frame_crop = resized.crop((off_x, off_y, off_x + size, off_y + size))

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(frame_crop, (0, 0), mask)

        d = ImageDraw.Draw(canvas)
        # Metallic luxury double border
        d.ellipse((1, 1, size - 2, size - 2), outline=(255, 255, 255, 220), width=3)
        d.ellipse((4, 4, size - 5, size - 5), outline=(79, 70, 229, 180), width=2)

        # Pulsating LIVE badge
        pulse = int(180 + 75 * math.sin(2 * math.pi * t * 2.0))
        bx, by = size - 76 - 12, 12
        d.rounded_rectangle([(bx, by), (bx + 76, by + 22)], radius=11, fill=(28, 28, 30, 220), outline=(255, 255, 255, 140), width=1)
        d.ellipse([(bx + 8, by + 6), (bx + 18, by + 16)], fill=(16, 185, 129, pulse))
        d.text((bx + 24, by + 4), "LIVE", font=font_sm, fill=(255, 255, 255, 240))

        # Bottom Nameplate Ribbon
        rx = 20
        ry = size - 28 - 10
        d.rounded_rectangle([(rx, ry), (rx + size - 40, ry + 28)], radius=14, fill=(19, 19, 20, 235), outline=(255, 255, 255, 120), width=1)
        d.text((rx + 14, ry + 7), preset["name"], font=font_name, fill=(255, 255, 255, 240))

        frame_path = os.path.join(temp_dir, f"f_{f:03d}.png")
        canvas.save(frame_path)

    # Encode with FFmpeg using qtrle (supports raw alpha transparency on Windows)
    ffmpeg_bin = find_ffmpeg()
    cmd = [
        ffmpeg_bin, "-y",
        "-framerate", str(fps),
        "-i", os.path.join(temp_dir, "f_%03d.png"),
        "-c:v", "qtrle",
        output_mov_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Clean up temp frames
    shutil.rmtree(temp_dir, ignore_errors=True)
    return output_mov_path


def generate_split_presenter_card(
    avatar_id: str,
    output_path: str,
    width: int = 540,
    height: int = 1920
) -> str:
    """
    Renders the left 540x1920 panel for Split-Screen mode:
    - High-res portrait framed in vertical aesthetic studio composition
    - Ambient blurred backdrop
    - Studio lighting gradient
    - Lower third verified doctor/creator credentials plate
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img_p = get_avatar_image_path(avatar_id)
    preset = AVATAR_PRESETS.get(avatar_id, AVATAR_PRESETS["uzma_creator"])

    card = Image.new("RGBA", (width, height), (19, 19, 20, 255))
    if os.path.exists(img_p):
        raw_img = Image.open(img_p).convert("RGBA")
        # Blurred atmospheric background
        bg_blur = raw_img.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=50))
        darkener = Image.new("RGBA", (width, height), (0, 0, 0, 130))
        bg_blur = Image.alpha_composite(bg_blur, darkener)
        card.paste(bg_blur, (0, 0))

        # Centered crisp portrait filling upper 65% of panel
        pw = int(width * 0.94)
        ph = pw
        portrait_crop = raw_img.resize((pw, ph), Image.Resampling.LANCZOS)
        
        # Soft bottom vignette fade
        fade_mask = Image.new("L", (pw, ph), 255)
        d_fade = ImageDraw.Draw(fade_mask)
        for i in range(180):
            alpha = int(255 * (1.0 - (i / 180.0)))
            d_fade.line([(0, ph - 180 + i), (pw, ph - 180 + i)], fill=alpha)
        
        px = (width - pw) // 2
        py = 180
        card.paste(portrait_crop, (px, py), fade_mask)
    
    d = ImageDraw.Draw(card)

    # Top Brand / Role Ribbon
    d.rounded_rectangle([(25, 70), (width - 25, 125)], radius=18, fill=(28, 28, 30, 220), outline=(255, 255, 255, 120), width=1)
    try:
        f_top = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 16)
        f_name = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 28)
        f_cred = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 16)
        f_desc = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 14)
    except Exception:
        f_top = f_name = f_cred = f_desc = ImageFont.load_default()

    d.ellipse([(45, 90), (59, 104)], fill=(16, 185, 129, 255))
    d.text((68, 86), "LIVE EXPERT PRESENTER", font=f_top, fill=(247, 245, 240, 255))

    # Lower Third Verified Credentials Plate
    ly = int(height * 0.58)
    lh = 480
    d.rounded_rectangle([(20, ly), (width - 20, ly + lh)], radius=26, fill=(19, 19, 20, 235), outline=(255, 255, 255, 110), width=1)

    # Verified Dot & Title
    d.ellipse([(40, ly + 32), (54, ly + 46)], fill=(16, 185, 129, 255))
    d.text((62, ly + 26), preset["badge"].upper(), font=f_top, fill=(16, 185, 129, 255))

    # Presenter Name
    d.text((40, ly + 68), preset["name"], font=f_name, fill=(247, 245, 240, 255))
    # Credentials
    d.text((40, ly + 110), preset["title"], font=f_cred, fill=(209, 213, 219, 255))
    d.text((40, ly + 138), preset["credentials"], font=f_desc, fill=(156, 163, 175, 255))

    # Live Waveform Bar
    d.line([(40, ly + 190), (width - 40, ly + 190)], fill=(255, 255, 255, 50), width=1)
    d.text((40, ly + 215), "AUTHENTIC CLINICAL ANALYSIS", font=f_top, fill=(129, 140, 248, 255))
    d.text((40, ly + 250), "100% Genuine Formula • COD PK", font=f_desc, fill=(156, 163, 175, 255))

    card.convert("RGB").save(output_path, "JPEG", quality=95)
    return output_path


def generate_fullscreen_presenter_card(
    avatar_id: str,
    output_path: str,
    scene_tag: str = "Live Creator Hook",
    headline: str = "Dermatologist Recommended Daily Routine",
    subtitle: str = "Official Clinical Formula Breakdown & Routine",
    width: int = 1080,
    height: int = 1920
) -> str:
    """
    Renders a dramatic, full-frame vertical 1080x1920 human presenter hero card.
    The real human character fills the entire upper 70% of the screen with natural
    depth of field, studio lighting, broadcast live badge, and high-contrast typography.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img_p = get_avatar_image_path(avatar_id)
    preset = AVATAR_PRESETS.get(avatar_id, AVATAR_PRESETS["uzma_creator"])

    card = Image.new("RGBA", (width, height), (19, 19, 20, 255))
    if os.path.exists(img_p):
        raw_img = Image.open(img_p).convert("RGBA")
        
        # 1. Background: ambient studio blurred glow
        bg_blur = raw_img.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=60))
        darkener = Image.new("RGBA", (width, height), (0, 0, 0, 130))
        bg_blur = Image.alpha_composite(bg_blur, darkener)
        card.paste(bg_blur, (0, 0))

        # 2. Main Presenter Hero: Scaled to fill upper 70% of frame naturally (1020x1020)
        pw = 1020
        ph = 1020
        portrait_crop = raw_img.resize((pw, ph), Image.Resampling.LANCZOS)

        # Soft bottom vignette fade so presenter body fades into the lower third naturally
        fade_mask = Image.new("L", (pw, ph), 255)
        d_fade = ImageDraw.Draw(fade_mask)
        for i in range(250):
            alpha = int(255 * (1.0 - (i / 250.0)))
            d_fade.line([(0, ph - 250 + i), (pw, ph - 250 + i)], fill=alpha)

        px = (width - pw) // 2
        py = 100
        card.paste(portrait_crop, (px, py), fade_mask)
    
    d = ImageDraw.Draw(card)

    # 3. Broadcast Top Pill
    d.rounded_rectangle([(40, 50), (width - 40, 115)], radius=26, fill=(28, 28, 30, 215), outline=(255, 255, 255, 90), width=1)

    try:
        font_top = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 20)
        font_title = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 44)
        font_sub = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 24)
        font_hook = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 30)
    except Exception:
        font_top = font_title = font_sub = font_hook = ImageFont.load_default()

    # Live green indicator dot
    d.ellipse([(65, 73), (85, 93)], fill=(16, 185, 129, 255))
    d.text((100, 68), f"LIVE BROADCAST • {scene_tag.upper()} • {preset['badge'].upper()}", font=font_top, fill=(247, 245, 240, 255))

    # 4. Luxury Lower Third Studio Card (Bottom 35%)
    by = 1240
    bh = 610
    d.rounded_rectangle([(40, by), (width - 40, by + bh)], radius=36, fill=(19, 19, 20, 235), outline=(255, 255, 255, 120), width=1)

    # Presenter Name & Credentials
    d.text((75, by + 45), preset["name"], font=font_title, fill=(247, 245, 240, 255))
    d.text((75, by + 105), f"{preset['title']} • {preset['credentials']}", font=font_sub, fill=(13, 148, 136, 255))

    d.line([(75, by + 160), (width - 75, by + 160)], fill=(255, 255, 255, 40), width=1)

    # Spoken Hook Subtitle Box
    d.text((75, by + 190), f'"{headline}"', font=font_hook, fill=(255, 255, 255, 255))
    d.text((75, by + 265), subtitle, font=font_sub, fill=(156, 163, 175, 255))

    # CTA Seal
    d.rounded_rectangle([(75, by + 370), (width - 75, by + 465)], radius=22, fill=(16, 185, 129, 230))
    d.text((140, by + 400), "● 100% VERIFIED AUTHENTIC BATCH • CASH ON DELIVERY PK", font=font_top, fill=(255, 255, 255, 255))

    card.convert("RGB").save(output_path, "JPEG", quality=95)
    return output_path
