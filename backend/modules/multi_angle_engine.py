import os
import math
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from backend.modules.avatar_engine import AVATAR_PRESETS, get_avatar_image_path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREATOR_FOOTAGE_DIR = os.path.join(PROJECT_ROOT, "storage", "creator_footage")
FONT_DIR = r"C:\Windows\Fonts"

CAMERA_ANGLES = {
    "angle_1_front_hook": {
        "id": "angle_1_front_hook",
        "name": "Angle 1: Front Eye-Contact (Hook)",
        "framing": "Medium Close-Up (Chest Up)",
        "camera_motion": "Cinematic Slow Push-In",
        "ffmpeg_filter": "zoompan=z='min(zoom+0.0008,1.06)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,fps=25",
        "purpose": "Stops scroll, direct eye contact with viewer, addresses acute pain point."
    },
    "angle_2_side_analysis": {
        "id": "angle_2_side_analysis",
        "name": "Angle 2: 45° Conversational Profile (Active Formula)",
        "framing": "3/4 Side Studio Angle",
        "camera_motion": "Smooth Horizontal Slider Drift",
        "ffmpeg_filter": "zoompan=z='1.04':d=125:x='if(lte(on,1),0,min(x+0.4,iw-iw/zoom))\':y='ih/2-(ih/zoom/2)':s=1080x1920,fps=25",
        "purpose": "Breaks visual fatigue, shows formula science and clinical ingredients."
    },
    "angle_3_macro_demo": {
        "id": "angle_3_macro_demo",
        "name": "Angle 3: Tight Macro Focus (Texture & Lather)",
        "framing": "Macro Close-Up on Hands & Skin",
        "camera_motion": "Gentle Floating Macro Zoom",
        "ffmpeg_filter": "zoompan=z='min(zoom+0.0012,1.08)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,fps=25",
        "purpose": "Sensory proof of non-sticky, foaming, or fast-absorbing application."
    },
    "angle_4_cta_hero": {
        "id": "angle_4_cta_hero",
        "name": "Angle 4: Dynamic Wide Punch-In (Closing CTA)",
        "framing": "Medium Wide Angle with COD Seal",
        "camera_motion": "Punchy Zoom-Out to Full Framing",
        "ffmpeg_filter": "zoompan=z='max(1.05-0.0007*on,1.00)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,fps=25",
        "purpose": "Final direct call-to-action, points to bio link, establishes COD trust."
    }
}

def get_creator_footage_clip(avatar_id: str, angle_index: int) -> str:
    """
    Checks if a real MP4 video clip exists in storage/creator_footage/{avatar_id}/angle_{N}.mp4.
    If custom real footage is present, returns its path.
    """
    avatar_dir = os.path.join(CREATOR_FOOTAGE_DIR, avatar_id)
    if os.path.exists(avatar_dir):
        patterns = [
            f"angle_{angle_index}.mp4",
            f"shot_{angle_index}.mp4",
            f"scene_{angle_index}.mp4"
        ]
        for p in patterns:
            v_path = os.path.join(avatar_dir, p)
            if os.path.exists(v_path) and os.path.getsize(v_path) > 10000:
                return v_path
    return None


def generate_transparent_scene_overlays(
    avatar_id: str,
    output_dir: str,
    item_id: str,
    script_data: dict,
    product_title: str = "",
    width: int = 1080,
    height: int = 1920
) -> list:
    """
    Generates 4 transparent PNG subtitle & branding overlay cards
    designed to sit on top of real full-motion human video clips.
    """
    os.makedirs(output_dir, exist_ok=True)
    preset = AVATAR_PRESETS.get(avatar_id, AVATAR_PRESETS.get("ayesha_derm", {}))
    p_name = preset.get("name", "Dr. Ayesha Khan")
    scenes = script_data.get("scenes", []) if script_data else []
    hook_text = script_data.get("hook", "Authentic Skincare Routine Analysis") if script_data else "Authentic Skincare Routine"

    try:
        font_pill = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 22)
        font_hook = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 38)
        font_sub = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 24)
        font_cta = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 22)
    except Exception:
        font_pill = font_hook = font_sub = font_cta = ImageFont.load_default()

    cam_configs = [
        {"cam": f"CAM 01: EYE-CONTACT HOOK • {p_name.upper()}", "tag": "SCENE 01 • DIRECT CREATOR HOOK", "dot": (16, 185, 129, 255)},
        {"cam": "CAM 02: CLINICAL ANALYSIS • FORMULA BREAKDOWN", "tag": "SCENE 02 • ACTIVE CLINICAL FORMULA", "dot": (79, 70, 229, 255)},
        {"cam": "CAM 03: SENSORY PROOF • TEXTURE & LATHER DEMO", "tag": "SCENE 03 • SENSORY APPLICATION", "dot": (234, 88, 12, 255)},
        {"cam": "CAM 04: CLOSING OFFER • COD VERIFIED PK", "tag": "SCENE 04 • SPECIAL OFFER & COD", "dot": (16, 185, 129, 255)}
    ]

    overlay_paths = []
    for i in range(4):
        p = os.path.join(output_dir, f"{item_id}_overlay_{i+1}.png")
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        cfg = cam_configs[i]
        # Top Broadcaster Pill
        d.rounded_rectangle([(40, 50), (width - 40, 115)], radius=26, fill=(19, 19, 20, 210), outline=(255, 255, 255, 80), width=1)
        d.ellipse([(65, 73), (85, 93)], fill=cfg["dot"])
        d.text((100, 68), cfg["cam"], font=font_pill, fill=(247, 245, 240, 255))

        # Bottom Frosted Subtitle Banner
        by = 1380
        bh = 460
        d.rounded_rectangle([(40, by), (width - 40, by + bh)], radius=32, fill=(15, 15, 18, 225), outline=(255, 255, 255, 90), width=1)
        d.text((75, by + 35), cfg["tag"], font=font_sub, fill=(16, 185, 129, 255))

        sub = ""
        if scenes and i < len(scenes) and scenes[i].get("subtitle"):
            sub = scenes[i].get("subtitle")
        elif i == 0:
            sub = hook_text
        else:
            sub = "Authentic clinical routine with guaranteed results."

        clean_sub = sub.strip()
        if len(clean_sub) > 65:
            mid = clean_sub.rfind(" ", 0, 55)
            if mid == -1: mid = 50
            line1 = clean_sub[:mid]
            line2 = clean_sub[mid:].strip()
            d.text((75, by + 85), f'"{line1}"', font=font_hook, fill=(255, 255, 255, 255))
            d.text((75, by + 140), f'"{line2}"', font=font_hook, fill=(255, 255, 255, 255))
        else:
            d.text((75, by + 100), f'"{clean_sub}"', font=font_hook, fill=(255, 255, 255, 255))

        prod_disp = product_title or "Verified Skincare"
        d.line([(75, by + 230), (width - 75, by + 230)], fill=(255, 255, 255, 40), width=1)
        d.text((75, by + 255), f"Featured: {prod_disp[:45]} • High Retention UGC Routine", font=font_sub, fill=(209, 213, 219, 255))

        # COD Verification Pill
        d.rounded_rectangle([(75, by + 330), (width - 75, by + 415)], radius=20, fill=(16, 185, 129, 235))
        d.text((120, by + 355), "● 100% VERIFIED AUTHENTIC BATCH • CASH ON DELIVERY PK", font=font_cta, fill=(255, 255, 255, 255))

        overlay.save(p, "PNG")
        overlay_paths.append(p)

    return overlay_paths



def generate_multi_angle_scene_cards(
    avatar_id: str,
    output_dir: str,
    item_id: str,
    script_data: dict,
    product_image_path: str = None,
    width: int = 1080,
    height: int = 1920
) -> list:
    """
    Renders 4 distinct, perspective-shifted camera angle visual cards for the video:
    - Scene 1: Angle 1 (Front Facing Hero Shot with direct eye contact)
    - Scene 2: Angle 2 (45° Side Conversational Perspective + Active Ingredients)
    - Scene 3: Angle 3 (Macro Texture Demo & Skin Application)
    - Scene 4: Angle 4 (Wide 3/4 Return to Creator with Closing COD Offer)
    """
    os.makedirs(output_dir, exist_ok=True)
    img_p = get_avatar_image_path(avatar_id)
    preset = AVATAR_PRESETS.get(avatar_id, AVATAR_PRESETS["ayesha_derm"])

    card_paths = []

    # Fonts
    try:
        font_pill = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 20)
        font_title = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 44)
        font_sub = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 24)
        font_hook = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 32)
        font_tag = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 16)
    except Exception:
        font_pill = font_title = font_sub = font_hook = font_tag = ImageFont.load_default()

    scenes = script_data.get("scenes", [])
    hook_text = script_data.get("hook", "Authentic Skincare Routine Analysis")
    if scenes and len(scenes) > 0 and scenes[0].get("subtitle"):
        hook_text = scenes[0].get("subtitle")

    # =========================================================================
    # SCENE 1 / ANGLE 1: FRONT EYE-CONTACT MEDIUM CLOSE-UP (THE HOOK)
    # =========================================================================
    s1_path = os.path.join(output_dir, f"{item_id}_angle_1_front.jpg")
    c1 = Image.new("RGBA", (width, height), (19, 19, 20, 255))
    if os.path.exists(img_p):
        raw_img = Image.open(img_p).convert("RGBA")
        bg1 = raw_img.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=60))
        c1.paste(Image.alpha_composite(bg1, Image.new("RGBA", (width, height), (0, 0, 0, 130))), (0, 0))

        # Centered Direct Front Framing
        pw, ph = 1020, 1020
        p_front = raw_img.resize((pw, ph), Image.Resampling.LANCZOS)
        fade_mask = Image.new("L", (pw, ph), 255)
        d_fade = ImageDraw.Draw(fade_mask)
        for i in range(250):
            d_fade.line([(0, ph - 250 + i), (pw, ph - 250 + i)], fill=int(255 * (1.0 - i/250.0)))
        c1.paste(p_front, ((width - pw) // 2, 100), fade_mask)

    d1 = ImageDraw.Draw(c1)
    # Camera Angle Indicator Badge
    d1.rounded_rectangle([(40, 50), (width - 40, 115)], radius=26, fill=(28, 28, 30, 220), outline=(255, 255, 255, 90), width=1)
    d1.ellipse([(65, 73), (85, 93)], fill=(16, 185, 129, 255))
    d1.text((100, 68), f"CAM 01: FRONT HOOK • {preset['name'].upper()} • {preset['badge'].upper()}", font=font_pill, fill=(247, 245, 240, 255))

    # Lower Third
    by = 1240
    d1.rounded_rectangle([(40, by), (width - 40, by + 610)], radius=36, fill=(19, 19, 20, 235), outline=(255, 255, 255, 120), width=1)
    d1.text((75, by + 45), preset["name"], font=font_title, fill=(247, 245, 240, 255))
    d1.text((75, by + 105), f"{preset['title']} • {preset['credentials']}", font=font_sub, fill=(13, 148, 136, 255))
    d1.line([(75, by + 160), (width - 75, by + 160)], fill=(255, 255, 255, 40), width=1)
    d1.text((75, by + 190), f'"{hook_text[:65]}"', font=font_hook, fill=(255, 255, 255, 255))
    d1.text((75, by + 265), "Official Clinical Formula Breakdown & Routine", font=font_sub, fill=(156, 163, 175, 255))
    d1.rounded_rectangle([(75, by + 370), (width - 75, by + 465)], radius=22, fill=(16, 185, 129, 230))
    d1.text((140, by + 400), "● 100% VERIFIED AUTHENTIC BATCH • CASH ON DELIVERY PK", font=font_pill, fill=(255, 255, 255, 255))

    c1.convert("RGB").save(s1_path, "JPEG", quality=95)
    card_paths.append(s1_path)

    # =========================================================================
    # SCENE 2 / ANGLE 2: 45° SIDE CONVERSATIONAL PROFILE (ACTIVE FORMULA)
    # =========================================================================
    s2_path = os.path.join(output_dir, f"{item_id}_angle_2_side.jpg")
    c2 = Image.new("RGBA", (width, height), (19, 19, 20, 255))
    if os.path.exists(img_p):
        raw_img = Image.open(img_p).convert("RGBA")
        bg2 = raw_img.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=55))
        c2.paste(Image.alpha_composite(bg2, Image.new("RGBA", (width, height), (0, 0, 0, 140))), (0, 0))

        # Offset framing to left simulating 45° conversational side angle
        pw2, ph2 = 720, 850
        # Horizontal flip or crop to create alternative perspective
        p_side = raw_img.transpose(Image.Transpose.FLIP_LEFT_RIGHT).resize((pw2, ph2), Image.Resampling.LANCZOS)
        fade2 = Image.new("L", (pw2, ph2), 255)
        d_f2 = ImageDraw.Draw(fade2)
        for i in range(200):
            d_f2.line([(0, ph2 - 200 + i), (pw2, ph2 - 200 + i)], fill=int(255 * (1.0 - i/200.0)))
        c2.paste(p_side, (30, 220), fade2)

    d2 = ImageDraw.Draw(c2)
    # Top Camera Indicator
    d2.rounded_rectangle([(40, 50), (width - 40, 115)], radius=26, fill=(28, 28, 30, 220), outline=(255, 255, 255, 90), width=1)
    d2.ellipse([(65, 73), (85, 93)], fill=(79, 70, 229, 255))
    d2.text((100, 68), "CAM 02: 45° SIDE ANGLE • ACTIVE FORMULA BREAKDOWN", font=font_pill, fill=(247, 245, 240, 255))

    # Right Side Formula Spec Spotlight Card
    rx = 520
    ry = 220
    rw = width - rx - 40
    rh = 750
    d2.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=28, fill=(28, 28, 30, 235), outline=(255, 255, 255, 120), width=1)
    d2.text((rx + 30, ry + 35), "ACTIVE FORMULA", font=font_tag, fill=(129, 140, 248, 255))
    
    ingredients = ["Ceramides 1, 3, 6-II", "Niacinamide (Vitamin B3)", "Salicylic Acid (BHA)", "Hyaluronic Acid Core"]
    for idx, ing in enumerate(ingredients):
        iy = ry + 85 + (idx * 110)
        d2.rounded_rectangle([(rx + 25, iy), (rx + rw - 25, iy + 85)], radius=18, fill=(19, 19, 20, 240), outline=(255, 255, 255, 60), width=1)
        d2.ellipse([(rx + 45, iy + 34), (rx + 60, iy + 49)], fill=(16, 185, 129, 255))
        d2.text((rx + 75, iy + 22), ing, font=font_sub, fill=(247, 245, 240, 255))
        d2.text((rx + 75, iy + 52), "Dermatologist Target Active", font=font_tag, fill=(156, 163, 175, 255))

    # Bottom Subtitle Banner
    by2 = 1240
    d2.rounded_rectangle([(40, by2), (width - 40, by2 + 580)], radius=36, fill=(19, 19, 20, 235), outline=(255, 255, 255, 120), width=1)
    d2.text((75, by2 + 45), "Clinical Mechanism & Action", font=font_title, fill=(247, 245, 240, 255))
    d2.text((75, by2 + 105), "Deep pore penetration restores barrier without stripping natural oils.", font=font_sub, fill=(209, 213, 219, 255))
    d2.line([(75, by2 + 160), (width - 75, by2 + 160)], fill=(255, 255, 255, 40), width=1)
    s2_sub = scenes[1].get("subtitle", "Zero harsh alcohols. 100% gentle barrier balance.") if len(scenes) > 1 else "Zero harsh alcohols. 100% gentle barrier balance."
    d2.text((75, by2 + 190), f'"{s2_sub[:65]}"', font=font_hook, fill=(129, 140, 248, 255))
    d2.rounded_rectangle([(75, by2 + 350), (width - 75, by2 + 440)], radius=20, fill=(28, 28, 30, 230), outline=(255, 255, 255, 90), width=1)
    d2.text((120, by2 + 375), "● NON-COMEDOGENIC • DERMATOLOGICALLY TESTED", font=font_pill, fill=(16, 185, 129, 255))

    c2.convert("RGB").save(s2_path, "JPEG", quality=95)
    card_paths.append(s2_path)

    # =========================================================================
    # SCENE 3 / ANGLE 3: TIGHT MACRO FOCUS (DEMONSTRATION & TEXTURE)
    # =========================================================================
    s3_path = os.path.join(output_dir, f"{item_id}_angle_3_demo.jpg")
    c3 = Image.new("RGBA", (width, height), (19, 19, 20, 255))
    if os.path.exists(img_p):
        raw_img = Image.open(img_p).convert("RGBA")
        bg3 = raw_img.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=50))
        c3.paste(Image.alpha_composite(bg3, Image.new("RGBA", (width, height), (0, 0, 0, 130))), (0, 0))

    d3 = ImageDraw.Draw(c3)
    # Top Camera Indicator
    d3.rounded_rectangle([(40, 50), (width - 40, 115)], radius=26, fill=(28, 28, 30, 220), outline=(255, 255, 255, 90), width=1)
    d3.ellipse([(65, 73), (85, 93)], fill=(234, 88, 12, 255))
    d3.text((100, 68), "CAM 03: MACRO DEMO • APPLICATION & SENSORY FOAM", font=font_pill, fill=(247, 245, 240, 255))

    # Central Macro Sensory Demo Showcase
    my = 220
    mw = width - 80
    mh = 950
    d3.rounded_rectangle([(40, my), (40 + mw, my + mh)], radius=36, fill=(28, 28, 30, 240), outline=(255, 255, 255, 120), width=1)

    # If user provided a real product photo, embed it crisp and large in center
    if product_image_path and os.path.exists(product_image_path):
        prod_img = Image.open(product_image_path).convert("RGBA")
        pw3 = 600
        ph3 = 600
        p_fit = prod_img.resize((pw3, ph3), Image.Resampling.LANCZOS)
        c3.paste(p_fit, ((width - pw3) // 2, my + 100), p_fit)
    else:
        # Elegant macro formula dropper graphic
        d3.rounded_rectangle([(width//2 - 160, my + 140), (width//2 + 160, my + 600)], radius=32, fill=(19, 19, 20, 240), outline=(255, 255, 255, 80), width=2)
        d3.text((width//2 - 110, my + 320), "AUTHENTIC BOTTLE", font=font_sub, fill=(156, 163, 175, 255))
        d3.ellipse([(width//2 - 50, my + 640), (width//2 + 50, my + 740)], fill=(129, 140, 248, 230))
        d3.text((width//2 - 95, my + 760), "Active Texture Swatch", font=font_tag, fill=(209, 213, 219, 255))

    # Lower Third Demo Subtitle
    by3 = 1240
    d3.rounded_rectangle([(40, by3), (width - 40, by3 + 580)], radius=36, fill=(19, 19, 20, 235), outline=(255, 255, 255, 120), width=1)
    d3.text((75, by3 + 45), "Sensory Proof & Feel", font=font_title, fill=(247, 245, 240, 255))
    s3_sub = scenes[2].get("subtitle", "1-minute gentle circular wash — Clean velvety matte finish!") if len(scenes) > 2 else "1-minute gentle circular wash — Clean velvety matte finish!"
    d3.text((75, by3 + 115), f'"{s3_sub[:65]}"', font=font_hook, fill=(255, 255, 255, 255))
    d3.line([(75, by3 + 195), (width - 75, by3 + 195)], fill=(255, 255, 255, 40), width=1)
    d3.text((75, by3 + 225), "Instant Results: Zero greasy film, pores cleared, skin feels hydrated.", font=font_sub, fill=(156, 163, 175, 255))
    d3.rounded_rectangle([(75, by3 + 340), (width - 75, by3 + 430)], radius=20, fill=(16, 185, 129, 230))
    d3.text((140, by3 + 365), "● CLINICALLY DEMONSTRATED RESULTS ACROSS PAKISTAN", font=font_pill, fill=(255, 255, 255, 255))

    c3.convert("RGB").save(s3_path, "JPEG", quality=95)
    card_paths.append(s3_path)

    # =========================================================================
    # SCENE 4 / ANGLE 4: DYNAMIC WIDE 3/4 ANGLE HERO (CLOSING CTA & COD)
    # =========================================================================
    s4_path = os.path.join(output_dir, f"{item_id}_angle_4_cta.jpg")
    c4 = Image.new("RGBA", (width, height), (19, 19, 20, 255))
    if os.path.exists(img_p):
        raw_img = Image.open(img_p).convert("RGBA")
        bg4 = raw_img.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=50))
        c4.paste(Image.alpha_composite(bg4, Image.new("RGBA", (width, height), (0, 0, 0, 120))), (0, 0))

        # Wide dynamic angle punch
        pw4, ph4 = 1040, 1040
        p_wide = raw_img.resize((pw4, ph4), Image.Resampling.LANCZOS)
        fade4 = Image.new("L", (pw4, ph4), 255)
        d_f4 = ImageDraw.Draw(fade4)
        for i in range(260):
            d_f4.line([(0, ph4 - 260 + i), (pw4, ph4 - 260 + i)], fill=int(255 * (1.0 - i/260.0)))
        c4.paste(p_wide, ((width - pw4) // 2, 80), fade4)

    d4 = ImageDraw.Draw(c4)
    # Top Camera Indicator
    d4.rounded_rectangle([(40, 50), (width - 40, 115)], radius=26, fill=(28, 28, 30, 220), outline=(255, 255, 255, 90), width=1)
    d4.ellipse([(65, 73), (85, 93)], fill=(16, 185, 129, 255))
    d4.text((100, 68), "CAM 04: WIDE CTA • OFFICIAL VERIFIED PURCHASE", font=font_pill, fill=(247, 245, 240, 255))

    # Bottom Studio Action Panel
    by4 = 1200
    d4.rounded_rectangle([(40, by4), (width - 40, by4 + 650)], radius=36, fill=(19, 19, 20, 240), outline=(255, 255, 255, 130), width=1)
    d4.text((75, by4 + 40), f"{preset['name']} Recommends", font=font_title, fill=(247, 245, 240, 255))
    d4.text((75, by4 + 100), "Do not compromise on counterfeit duplicates.", font=font_sub, fill=(209, 213, 219, 255))
    d4.line([(75, by4 + 155), (width - 75, by4 + 155)], fill=(255, 255, 255, 40), width=1)

    d4.text((75, by4 + 185), "Get 100% Original Sealed Tube Today", font=font_hook, fill=(129, 140, 248, 255))
    d4.text((75, by4 + 250), "Fast Dispatch to Karachi, Lahore, Islamabad & All Cities", font=font_sub, fill=(156, 163, 175, 255))

    # Big CTA Button
    d4.rounded_rectangle([(75, by4 + 320), (width - 75, by4 + 430)], radius=24, fill=(16, 185, 129, 240))
    d4.text((120, by4 + 355), "TAP LINK IN BIO • ORDER ORIGINAL WITH COD", font=font_pill, fill=(255, 255, 255, 255))

    d4.text((75, by4 + 465), "Verified Authentic Guarantee • 7-Day Easy Return Policy", font=font_sub, fill=(156, 163, 175, 255))

    c4.convert("RGB").save(s4_path, "JPEG", quality=95)
    card_paths.append(s4_path)

    return card_paths
