import os
import textwrap
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

def _get_font(size: int, bold: bool = True):
    try:
        font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
        font_path = os.path.join(r"C:\Windows\Fonts", font_name)
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        fallback = os.path.join(r"C:\Windows\Fonts", "arialbd.ttf" if bold else "arial.ttf")
        if os.path.exists(fallback):
            return ImageFont.truetype(fallback, size)
    except Exception:
        pass
    return ImageFont.load_default()

def _round_corners(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    result = img.copy()
    result.putalpha(mask)
    return result

def _has_transparency(img: Image.Image) -> bool:
    if img.mode != "RGBA":
        return False
    extrema = img.getextrema()
    if len(extrema) >= 4 and extrema[3][0] < 250:
        return True
    return False

def contains_arabic_or_urdu(text: str) -> bool:
    for char in text:
        if ('\u0600' <= char <= '\u06FF' or 
            '\u0750' <= char <= '\u077F' or 
            '\uFB50' <= char <= '\uFDFF' or 
            '\uFE70' <= char <= '\uFEFF'):
            return True
    return False

def sanitize_canvas_text(text: str, fallback: str = "Premium Authentic Skincare") -> str:
    """
    Windows PIL cannot shape Arabic/Urdu script without libraqm, causing
    reversed and disconnected glyphs. For on-screen visual banners and subtitles,
    if text contains Arabic/Urdu script, provide a clean, high-converting English/Roman claim.
    """
    if not text or not str(text).strip():
        return fallback
    clean = str(text).strip()
    if contains_arabic_or_urdu(clean):
        return fallback
    return clean

def create_aesthetic_card(
    title: str, 
    subtitle: str, 
    action_text: str,
    active_subtitle_text: str,
    output_path: str,
    theme: str = "rose_sunset",
    product_image_path: Optional[str] = None
) -> str:
    """
    Generates a 1080x1920 luxury vertical visual canvas with Segoe UI typography,
    real product photo integration (with automatic alpha transparency / spotlight pedestal),
    action banner, and burned-in lower third subtitles bar.
    """
    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), color="#0F172A")
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_brand = _get_font(24, bold=True)
    font_action = _get_font(26, bold=True)
    font_badge = _get_font(20, bold=True)
    font_subtitle_label = _get_font(22, bold=True)
    font_subtitle_text = _get_font(28, bold=True)
    font_trust = _get_font(24, bold=True)
    font_sub = _get_font(26, bold=False)

    # Color Schemes
    if theme == "mens":
        top_color = (20, 14, 28)         # Deep Violet Slate
        mid_color = (45, 20, 44)         # Rich Plum
        bottom_color = (15, 23, 42)      # Dark Charcoal
        accent = (251, 146, 60)          # Vibrant Sunset Orange
        accent_secondary = (244, 63, 94) # Rose Red
    else: # Rose & Warm Orange Sunset Glow (Default)
        top_color = (36, 12, 34)         # Deep Rose Plum
        mid_color = (70, 20, 40)         # Rich Wine
        bottom_color = (20, 15, 25)      # Obsidian
        accent = (251, 146, 60)          # Warm Vibrant Orange
        accent_secondary = (244, 114, 182) # Luminous Rose Pink
        
    # Draw smooth gradient across 1920 vertical pixels
    for y in range(height):
        ratio = y / height
        if ratio < 0.5:
            local_ratio = ratio / 0.5
            r = int(top_color[0] * (1 - local_ratio) + mid_color[0] * local_ratio)
            g = int(top_color[1] * (1 - local_ratio) + mid_color[1] * local_ratio)
            b = int(top_color[2] * (1 - local_ratio) + mid_color[2] * local_ratio)
        else:
            local_ratio = (ratio - 0.5) / 0.5
            r = int(mid_color[0] * (1 - local_ratio) + bottom_color[0] * local_ratio)
            g = int(mid_color[1] * (1 - local_ratio) + bottom_color[1] * local_ratio)
            b = int(mid_color[2] * (1 - local_ratio) + bottom_color[2] * local_ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Top Brand Ribbon
    draw.rounded_rectangle([80, 65, 1000, 145], radius=24, fill=(15, 10, 20), outline=accent, width=2)
    draw.text((120, 90), "LUMIÈRE STUDIO • VERTICAL REEL", fill=accent, font=font_brand)
    
    # Main Outer Glassmorphism Card (y: 165 to 1690 - leaves bottom 230px safe zone)
    card_x0, card_y0 = 60, 165
    card_x1, card_y1 = 1020, 1690
    draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=40, fill=(20, 10, 25), outline=accent_secondary, width=3)
    
    # Glowing Model Action Badge (Pill)
    draw.rounded_rectangle([100, 205, 980, 285], radius=20, fill=accent)
    action_disp = f"DEMONSTRATION: {action_text.upper()[:42]}"
    draw.text((130, 232), action_disp, fill=(15, 23, 42), font=font_action)
    
    # Title - Dynamic Auto-Scaling & Word-Wrapping so long names are never cut off
    clean_title = sanitize_canvas_text(title, fallback="Authentic Beauty Formula")
    if len(clean_title) > 28:
        font_title = _get_font(36, bold=True)
        title_lines = textwrap.wrap(clean_title, width=28)
        if len(title_lines) > 2:
            title_lines = title_lines[:2]
            title_lines[1] = textwrap.shorten(title_lines[1], width=26, placeholder="...")
        title_disp = "\n".join(title_lines)
        title_y = 315
        sub_y = 315 + (len(title_lines) * 44) + 8
    else:
        font_title = _get_font(44, bold=True)
        title_disp = clean_title
        title_y = 325
        sub_y = 385

    draw.multiline_text((100, title_y), title_disp, fill=(255, 255, 255), font=font_title, spacing=6)
    
    # Subtitle Hook - Safe Typography & Clean Wrapping
    safe_sub = sanitize_canvas_text(subtitle, fallback="Instant Radiance & Fast Absorbing Cellular Care")
    sub_lines = textwrap.wrap(safe_sub, width=48)
    if len(sub_lines) > 2:
        sub_lines = sub_lines[:2]
        sub_lines[1] = textwrap.shorten(sub_lines[1], width=45, placeholder="...")
    sub_disp = "\n".join(sub_lines)
    draw.multiline_text((100, sub_y), sub_disp, fill=(253, 186, 116), font=font_sub, spacing=4)
    
    # Center Showcase Frame (Product & Demonstration Zone)
    # y: 500 to 1340 (Height: 840px, Width: 880px)
    show_x0, show_y0 = 100, 500
    show_x1, show_y1 = 980, 1340
    draw.rounded_rectangle([show_x0, show_y0, show_x1, show_y1], radius=32, fill=(12, 6, 16), outline=accent, width=2)
    
    # Dedicated Header Zone inside Showcase Frame for Badges (y: 520 to 570)
    # Verified Product Badge Pill
    badge_x0, badge_y0 = show_x0 + 25, show_y0 + 20
    badge_x1, badge_y1 = show_x0 + 360, show_y0 + 68
    draw.rounded_rectangle([badge_x0, badge_y0, badge_x1, badge_y1], radius=16, fill=(15, 23, 42), outline=accent, width=1)
    draw.ellipse([badge_x0 + 18, badge_y0 + 17, badge_x0 + 32, badge_y0 + 31], fill=(34, 197, 94))
    draw.text((badge_x0 + 44, badge_y0 + 13), "VERIFIED PRODUCT PHOTO", fill=(241, 245, 249), font=font_badge)

    # Right batch authenticity tag
    auth_x0 = show_x1 - 250
    draw.rounded_rectangle([auth_x0, badge_y0, show_x1 - 25, badge_y1], radius=16, fill=(25, 12, 28), outline=(244, 114, 182), width=1)
    draw.text((auth_x0 + 24, badge_y0 + 14), "100% ORIGINAL", fill=(244, 114, 182), font=font_badge)

    # Product Display Area starts strictly BELOW the badges: y = 585 to 1320 (Height ~735px)
    prod_area_y0 = show_y0 + 80
    prod_area_y1 = show_y1 - 25
    prod_area_h = prod_area_y1 - prod_area_y0
    box_w = show_x1 - show_x0
    
    real_photo_drawn = False
    if product_image_path and os.path.exists(product_image_path):
        try:
            prod_img = Image.open(product_image_path)
            prod_rgba = prod_img.convert("RGBA")
            
            # Max dimensions for product display inside dedicated area
            max_p_w = box_w - 120   # ~760px
            max_p_h = prod_area_h - 40  # ~690px
            
            orig_w, orig_h = prod_rgba.size
            scale = min(max_p_w / orig_w, max_p_h / orig_h)
            new_w = max(10, int(orig_w * scale))
            new_h = max(10, int(orig_h * scale))
            
            resized_p = prod_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Centered position in the dedicated product area
            center_x = (show_x0 + show_x1) // 2
            pos_x = center_x - new_w // 2
            center_y = (prod_area_y0 + prod_area_y1) // 2
            pos_y = center_y - new_h // 2
            
            is_transparent = _has_transparency(resized_p)
            
            if is_transparent:
                # Studio spotlight pedestal for transparent cutouts
                pedestal_y = prod_area_y1 - 40
                draw.ellipse([center_x - 280, pedestal_y - 22, center_x + 280, pedestal_y + 22], fill=(251, 146, 60, 80), outline=accent, width=2)
                draw.ellipse([center_x - 200, pedestal_y - 10, center_x + 200, pedestal_y + 10], fill=(255, 237, 213, 120))
                pos_y = pedestal_y - new_h + 10
                img.paste(resized_p, (pos_x, pos_y), resized_p)
            else:
                # Solid photo - wrap in a luxury presentation podium card so white borders look intentional
                pad = 14
                podium_box = [pos_x - pad, pos_y - pad, pos_x + new_w + pad, pos_y + new_h + pad]
                draw.rounded_rectangle(podium_box, radius=24, fill=(255, 255, 255), outline=accent, width=2)
                
                rounded_p = _round_corners(resized_p, radius=18)
                img.paste(rounded_p, (pos_x, pos_y), rounded_p)
                
            real_photo_drawn = True
        except Exception as e:
            print(f"Warning: Failed to render product photo {product_image_path}: {e}")
            real_photo_drawn = False
            
    if not real_photo_drawn:
        # Luxury procedural product blueprint silhouette
        cx = (show_x0 + show_x1) // 2
        cy = (prod_area_y0 + prod_area_y1) // 2
        
        # Studio Spotlight Pedestal
        draw.ellipse([cx - 260, cy + 180, cx + 260, cy + 240], fill=(251, 146, 60, 40), outline=accent, width=2)
        draw.ellipse([cx - 170, cy + 195, cx + 170, cy + 225], fill=(254, 215, 170, 70))
        
        # Cosmetic Dispenser Bottle Blueprint
        draw.rounded_rectangle([cx - 85, cy - 110, cx + 85, cy + 180], radius=24, fill=(25, 12, 30), outline=accent, width=3)
        draw.rounded_rectangle([cx - 65, cy - 30, cx + 65, cy + 160], radius=14, fill=(251, 146, 60, 40))
        # Bottle Neck & Cap
        draw.rounded_rectangle([cx - 32, cy - 165, cx + 32, cy - 110], radius=8, fill=(40, 18, 48), outline=accent, width=2)
        draw.rounded_rectangle([cx - 22, cy - 200, cx + 22, cy - 165], radius=6, fill=accent)
        
        draw.text((cx - 200, cy + 260), "PREMIUM PACKAGING & FORMULA", fill=accent, font=font_subtitle_label)
        draw.text((cx - 180, cy + 300), "(Authentic Batch • Verified Origin)", fill=(203, 213, 225), font=font_sub)

    # Lower-Third Subtitle Bar (High-Contrast Bold Subtitles)
    # y: 1365 to 1515 (Height: 150px)
    sub_box_y0 = 1365
    sub_box_y1 = 1515
    draw.rounded_rectangle([100, sub_box_y0, 980, sub_box_y1], radius=24, fill=(10, 5, 15), outline=accent, width=2)
    draw.text((130, sub_box_y0 + 18), "LIVE DEMONSTRATION SUBTITLE:", fill=accent, font=font_subtitle_label)
    
    raw_sub = active_subtitle_text if active_subtitle_text else "Order genuine batch via direct bio link!"
    safe_active_sub = sanitize_canvas_text(raw_sub, fallback="Order genuine batch via direct bio link!")
    sub_disp_lines = textwrap.wrap(f'"{safe_active_sub}"', width=46)
    if len(sub_disp_lines) > 2:
        sub_disp_lines = sub_disp_lines[:2]
        sub_disp_lines[1] = textwrap.shorten(sub_disp_lines[1], width=42, placeholder='..."')
    draw.multiline_text((130, sub_box_y0 + 55), "\n".join(sub_disp_lines), fill=(255, 255, 255), font=font_subtitle_text, spacing=4)
    
    # Bottom Trust & Verified Badge (y: 1540 to 1625 - Height: 85px)
    # Safe zone from 1625 to 1920 (295px) ensures video player controls NEVER obscure the badge!
    trust_y0 = 1540
    trust_y1 = 1625
    draw.rounded_rectangle([100, trust_y0, 980, trust_y1], radius=20, fill=(20, 80, 42), outline=(34, 197, 94), width=2)
    draw.text((180, trust_y0 + 26), "VERIFIED AUTHENTIC BATCH • CASH ON DELIVERY PK", fill=(255, 255, 255), font=font_trust)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    return output_path


def create_multi_scene_cards(
    script_data: dict,
    output_dir: str,
    item_id: str,
    theme: str = "rose_sunset",
    product_image_path: Optional[str] = None
) -> list:
    """
    Generates 4 distinct 1080x1920 luxury scene cards for multi-scene animated video rendering:
      - Scene 1: Viral Hook & Product Discovery
      - Scene 2: Active Formula & Ingredient Breakdown
      - Scene 3: Physical Sensory Demonstration & How-To Steps
      - Scene 4: High-Conversion Call To Action & Limited Direct Offer
    """
    os.makedirs(output_dir, exist_ok=True)
    scenes = script_data.get("scenes", [])
    product_name = script_data.get("product_name", "Authentic Beauty Care")
    action_desc = script_data.get("action_description", "Model Application")
    detected_form = script_data.get("detected_form", "beauty_care").replace("_", " ").upper()
    
    # Fallback scenes if fewer than 4
    while len(scenes) < 4:
        idx = len(scenes) + 1
        scenes.append({
            "n": idx,
            "title": f"Scene {idx}",
            "subtitle": f"Authentic Experience • Scene {idx}",
            "on_screen_text": "Verified Formula"
        })
        
    width, height = 1080, 1920
    
    # Theme colors
    if theme == "mens":
        top_color = (20, 14, 28)
        mid_color = (45, 20, 44)
        bottom_color = (15, 23, 42)
        accent = (251, 146, 60)          # Vibrant Sunset Orange
        accent_secondary = (244, 63, 94) # Rose Red
    else:
        top_color = (36, 12, 34)
        mid_color = (70, 20, 40)
        bottom_color = (20, 15, 25)
        accent = (251, 146, 60)          # Warm Vibrant Orange
        accent_secondary = (244, 114, 182) # Luminous Rose Pink

    font_brand = _get_font(24, bold=True)
    font_badge = _get_font(20, bold=True)
    font_sub_label = _get_font(22, bold=True)
    font_sub_text = _get_font(28, bold=True)
    font_trust = _get_font(24, bold=True)
    font_sub = _get_font(26, bold=False)
    font_headline = _get_font(38, bold=True)
    font_btn = _get_font(32, bold=True)
    font_step = _get_font(24, bold=True)

    generated_paths = []
    
    for i in range(4):
        scene = scenes[i]
        scene_num = i + 1
        output_path = os.path.join(output_dir, f"{item_id}_scene_{scene_num}.jpg")
        
        img = Image.new("RGB", (width, height), color="#0F172A")
        draw = ImageDraw.Draw(img)
        
        # 1. Background Gradient
        for y in range(height):
            ratio = y / height
            if ratio < 0.5:
                lr = ratio / 0.5
                r = int(top_color[0] * (1 - lr) + mid_color[0] * lr)
                g = int(top_color[1] * (1 - lr) + mid_color[1] * lr)
                b = int(top_color[2] * (1 - lr) + mid_color[2] * lr)
            else:
                lr = (ratio - 0.5) / 0.5
                r = int(mid_color[0] * (1 - lr) + bottom_color[0] * lr)
                g = int(mid_color[1] * (1 - lr) + bottom_color[1] * lr)
                b = int(mid_color[2] * (1 - lr) + bottom_color[2] * lr)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
            
        # 2. Top Header Ribbon with Dynamic Progress Indicator
        draw.rounded_rectangle([80, 65, 1000, 145], radius=24, fill=(15, 10, 20), outline=accent, width=2)
        step_dots = " ".join(["●" if (j + 1) == scene_num else "○" for j in range(4)])
        header_text = f"LUMIÈRE AI • {step_dots}  SCENE {scene_num} OF 4"
        draw.text((120, 90), header_text, fill=accent, font=font_brand)
        
        # 3. Outer Glassmorphism Card (y: 165 to 1690)
        card_x0, card_y0 = 60, 165
        card_x1, card_y1 = 1020, 1690
        draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=40, fill=(20, 10, 25), outline=accent_secondary, width=3)
        
        # 4. Scene Type Badge Pill (y: 205 to 285)
        draw.rounded_rectangle([100, 205, 980, 285], radius=20, fill=accent)
        if scene_num == 1:
            pill_label = f"VIRAL DISCOVERY • {detected_form}"
        elif scene_num == 2:
            pill_label = "ACTIVE FORMULATION & CELLULAR BENEFITS"
        elif scene_num == 3:
            pill_label = f"SENSORY DEMONSTRATION • {action_desc.upper()[:36]}"
        else:
            pill_label = "EXCLUSIVE DIRECT OFFER • LIMITED STOCK"
        draw.text((130, 232), pill_label, fill=(15, 23, 42), font=_get_font(24, bold=True))
        
        # 5. Dynamic Scene Headline (y: 310 to 470)
        raw_headline = scene.get("subtitle") or scene.get("on_screen_text") or product_name
        clean_headline = sanitize_canvas_text(raw_headline, fallback=product_name)
        wrapped_headline = textwrap.wrap(clean_headline, width=36)
        if len(wrapped_headline) > 2:
            wrapped_headline = wrapped_headline[:2]
            wrapped_headline[1] = textwrap.shorten(wrapped_headline[1], width=33, placeholder="...")
        draw.multiline_text((100, 315), "\n".join(wrapped_headline), fill=(255, 255, 255), font=font_headline, spacing=6)
        
        product_title_sub = sanitize_canvas_text(product_name, fallback="Genuine E-Commerce Formula")
        draw.text((100, 425), f"Product Focus: {product_title_sub[:48]}", fill=(253, 186, 116), font=font_sub)
        
        # 6. Center Feature & Product Showcase Frame (y: 480 to 1340)
        show_x0, show_y0 = 100, 480
        show_x1, show_y1 = 980, 1340
        draw.rounded_rectangle([show_x0, show_y0, show_x1, show_y1], radius=32, fill=(12, 6, 16), outline=accent, width=2)
        
        # Badges inside Showcase Frame
        draw.rounded_rectangle([show_x0 + 25, show_y0 + 20, show_x0 + 380, show_y0 + 68], radius=16, fill=(15, 23, 42), outline=accent, width=1)
        draw.ellipse([show_x0 + 42, show_y0 + 36, show_x0 + 56, show_y0 + 50], fill=(34, 197, 94))
        draw.text((show_x0 + 68, show_y0 + 32), f"SCENE 0{scene_num} SPOTLIGHT", fill=(241, 245, 249), font=font_badge)
        
        auth_x0 = show_x1 - 250
        draw.rounded_rectangle([auth_x0, show_y0 + 20, show_x1 - 25, show_y0 + 68], radius=16, fill=(25, 12, 28), outline=(244, 114, 182), width=1)
        draw.text((auth_x0 + 24, show_y0 + 34), "100% ORIGINAL", fill=(244, 114, 182), font=font_badge)

        # Center Graphic Area (y: 560 to 1320)
        center_x = (show_x0 + show_x1) // 2
        prod_area_y0 = show_y0 + 75
        prod_area_y1 = show_y1 - 25
        
        # Product Photo Rendering
        real_photo_drawn = False
        if product_image_path and os.path.exists(product_image_path):
            try:
                prod_img = Image.open(product_image_path).convert("RGBA")
                orig_w, orig_h = prod_img.size
                
                # Sizing depends on scene type:
                # In scene 2 & 4, leave room for benefit cards/CTA button
                if scene_num in [2, 4]:
                    max_w = 480
                    max_h = 360
                    center_y = prod_area_y0 + 200
                else:
                    max_w = 640
                    max_h = 580
                    center_y = (prod_area_y0 + prod_area_y1) // 2
                    
                scale = min(max_w / orig_w, max_h / orig_h)
                new_w = max(10, int(orig_w * scale))
                new_h = max(10, int(orig_h * scale))
                resized_p = prod_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                pos_x = center_x - new_w // 2
                pos_y = center_y - new_h // 2
                
                if _has_transparency(resized_p):
                    ped_y = pos_y + new_h
                    draw.ellipse([center_x - 240, ped_y - 18, center_x + 240, ped_y + 18], fill=(251, 146, 60, 80), outline=accent, width=2)
                    img.paste(resized_p, (pos_x, pos_y), resized_p)
                else:
                    pad = 10
                    draw.rounded_rectangle([pos_x - pad, pos_y - pad, pos_x + new_w + pad, pos_y + new_h + pad], radius=20, fill=(255, 255, 255), outline=accent, width=2)
                    rounded_p = _round_corners(resized_p, radius=16)
                    img.paste(rounded_p, (pos_x, pos_y), rounded_p)
                real_photo_drawn = True
            except Exception as e:
                print(f"Warning: Failed to render product photo in scene {scene_num}: {e}")
                real_photo_drawn = False

        if not real_photo_drawn:
            # Procedural Luxury Silhouette Bottle
            cy = (prod_area_y0 + prod_area_y1) // 2 if scene_num not in [2, 4] else prod_area_y0 + 200
            draw.ellipse([center_x - 220, cy + 140, center_x + 220, cy + 190], fill=(251, 146, 60, 40), outline=accent, width=2)
            draw.rounded_rectangle([center_x - 70, cy - 80, center_x + 70, cy + 140], radius=20, fill=(25, 12, 30), outline=accent, width=2)
            draw.rounded_rectangle([center_x - 25, cy - 120, center_x + 25, cy - 80], radius=6, fill=accent)

        # Scene-Specific Overlays in the lower half of showcase frame
        if scene_num == 1:
            # SCENE 1: Problem / Viral Discovery Callout
            draw.rounded_rectangle([show_x0 + 50, show_y1 - 120, show_x1 - 50, show_y1 - 25], radius=18, fill=(25, 12, 32), outline=accent, width=2)
            draw.text((show_x0 + 80, show_y1 - 100), "TIKTOK & REELS VIRAL SENSATION IN PAKISTAN", fill=(255, 255, 255), font=font_step)
            draw.text((show_x0 + 80, show_y1 - 65), "High Retention Routine • Authentic Dermatological Formula", fill=(253, 186, 116), font=_get_font(20, bold=False))

        elif scene_num == 2:
            # SCENE 2: 3 Benefits Feature Badges
            b_y0 = show_y0 + 440
            benefits = [
                ("NON-GREASY ABSORPTION", "Deep cellular penetration without sticky residue"),
                ("ACTIVE BARRIER RESTORATION", "Ceramides & moisture seal for 24-hour protection"),
                ("DERMATOLOGIST TESTED", "100% gentle on sensitive skin • Zero harsh chemicals")
            ]
            for b_idx, (b_title, b_desc) in enumerate(benefits):
                box_top = b_y0 + (b_idx * 115)
                draw.rounded_rectangle([show_x0 + 40, box_top, show_x1 - 40, box_top + 95], radius=16, fill=(18, 10, 24), outline=accent if b_idx == 0 else accent_secondary, width=1)
                draw.ellipse([show_x0 + 60, box_top + 28, show_x0 + 95, box_top + 63], fill=(34, 197, 94))
                draw.text((show_x0 + 72, box_top + 33), "✓", fill=(255, 255, 255), font=_get_font(22, bold=True))
                draw.text((show_x0 + 115, box_top + 22), b_title, fill=(255, 255, 255), font=font_step)
                draw.text((show_x0 + 115, box_top + 55), b_desc, fill=(203, 213, 225), font=_get_font(18, bold=False))

        elif scene_num == 3:
            # SCENE 3: How-To Sensory Step Instructions
            draw.rounded_rectangle([show_x0 + 40, show_y1 - 145, show_x1 - 40, show_y1 - 25], radius=18, fill=(15, 23, 42), outline=(34, 197, 94), width=2)
            draw.text((show_x0 + 70, show_y1 - 128), "APPLICATION STEP: SENSORY ABSORPTION", fill=(34, 197, 94), font=font_sub_label)
            step_instruction = f"Apply as directed: {action_desc[:55]}"
            draw.text((show_x0 + 70, show_y1 - 90), step_instruction, fill=(255, 255, 255), font=_get_font(22, bold=True))
            draw.text((show_x0 + 70, show_y1 - 58), "Leaves skin velvety smooth with zero greasy shine.", fill=(203, 213, 225), font=_get_font(18, bold=False))

        elif scene_num == 4:
            # SCENE 4: High-Converting CTA Button & COD Badges
            cta_box_y0 = show_y0 + 470
            # Big Vibrant Call to Action Button
            draw.rounded_rectangle([show_x0 + 40, cta_box_y0, show_x1 - 40, cta_box_y0 + 110], radius=24, fill=accent, outline=(255, 255, 255), width=2)
            draw.text((show_x0 + 110, cta_box_y0 + 36), "ORDER NOW • TAP LINK IN BIO", fill=(15, 23, 42), font=font_btn)
            
            # Trust & COD Info
            draw.rounded_rectangle([show_x0 + 40, cta_box_y0 + 130, show_x1 - 40, cta_box_y0 + 230], radius=18, fill=(22, 10, 28), outline=(34, 197, 94), width=1)
            draw.text((show_x0 + 70, cta_box_y0 + 150), "★ CASH ON DELIVERY AVAILABLE NATIONWIDE", fill=(34, 197, 94), font=font_step)
            draw.text((show_x0 + 70, cta_box_y0 + 185), "Express 2-3 Day Doorstep Delivery across Pakistan", fill=(241, 245, 249), font=_get_font(20, bold=False))

        # 7. Lower-Third Subtitle Bar (High-Contrast Bold Subtitles for this Scene)
        sub_box_y0 = 1365
        sub_box_y1 = 1515
        draw.rounded_rectangle([100, sub_box_y0, 980, sub_box_y1], radius=24, fill=(10, 5, 15), outline=accent, width=2)
        draw.text((130, sub_box_y0 + 18), f"SCENE 0{scene_num} LIVE VOICE SUBTITLE:", fill=accent, font=font_sub_label)
        
        scene_sub = scene.get("subtitle") or scene.get("on_screen_text") or "Genuine skincare solution"
        safe_active_sub = sanitize_canvas_text(scene_sub, fallback="Genuine beauty formula in Pakistan")
        sub_disp_lines = textwrap.wrap(f'"{safe_active_sub}"', width=46)
        if len(sub_disp_lines) > 2:
            sub_disp_lines = sub_disp_lines[:2]
            sub_disp_lines[1] = textwrap.shorten(sub_disp_lines[1], width=42, placeholder='..."')
        draw.multiline_text((130, sub_box_y0 + 55), "\n".join(sub_disp_lines), fill=(255, 255, 255), font=font_sub_text, spacing=4)
        
        # 8. Bottom Trust & Verified Badge
        trust_y0 = 1540
        trust_y1 = 1625
        draw.rounded_rectangle([100, trust_y0, 980, trust_y1], radius=20, fill=(20, 80, 42), outline=(34, 197, 94), width=2)
        if scene_num == 4:
            trust_txt = "VERIFIED SELLER • CASH ON DELIVERY PK • ORDER NOW"
        elif scene_num == 2:
            trust_txt = "DERMATOLOGICALLY TESTED • ZERO HARSH CHEMICALS"
        else:
            trust_txt = "VERIFIED AUTHENTIC BATCH • CASH ON DELIVERY PK"
        draw.text((170, trust_y0 + 26), trust_txt, fill=(255, 255, 255), font=font_trust)
        
        img.save(output_path, quality=95)
        generated_paths.append(output_path)
        
    return generated_paths


if __name__ == "__main__":
    out = r"F:\Projects\beauty-marketing-agent\storage\raw_assets\test_rose_card.jpg"
    test_img = r"F:\Projects\beauty-marketing-agent\storage\raw_assets\uploads\url_21a2a004.jpg"
    create_aesthetic_card(
        title="Garnier Bright Complete Vitamin C Booster Serum", 
        subtitle="Stubborn spots, open pores, and dull complexion?", 
        action_text="Face Application", 
        active_subtitle_text="Just 2 drops — lightweight dewy absorption", 
        output_path=out,
        product_image_path=test_img
    )
    print("Created upgraded card:", out)
