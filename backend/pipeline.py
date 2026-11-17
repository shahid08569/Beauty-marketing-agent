import os
import sys
import json
import time
import uuid

# Ensure root project directory is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.modules.ai_brain import generate_script_with_ai
from backend.modules.compliance_checker import check_compliance
from backend.modules.tts_engine import generate_voiceover, AVAILABLE_VOICES
from backend.modules.media_fetcher import create_aesthetic_card, create_multi_scene_cards
from backend.modules.video_renderer import render_vertical_video, render_multi_scene_video
from backend.modules.publisher import create_export_pack

DB_PATH = r"F:\Projects\beauty-marketing-agent\storage\database.json"

def _load_db() -> list:
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_db(data: list):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run_pipeline(
    product_prompt: str,
    category: str = "beauty_skincare",
    target_gender: str = "women",
    language: str = "roman_urdu",
    action_type: str = "face_application",
    voice_key: str = "swara_influencer",
    target_duration: int = 30,
    ai_model: str = "auto_smart",
    custom_api_key: str = None,
    date_range_type: str = "last_7_days",
    start_date: str = None,
    end_date: str = None,
    product_image_path: str = None,
    bgm_track: str = "lofi_chill",
    avatar_character: str = "none",
    avatar_layout: str = "intro_outro",
    heygen_api_key: str = None,
    custom_script: dict = None,
    supermodel_id: str = None,
    hairstyle: str = "Natural",
    wardrobe: str = "Standard",
    video_engine_provider: str = "local",
    video_engine_model: str = "kling",
    video_engine_key: str = None
) -> dict:
    item_id = f"item_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    print(f"[*] Starting Pipeline for {product_prompt} (AI: {ai_model}, Range: {date_range_type}, Duration: {target_duration}s, BGM: {bgm_track})...")
    
    # 1. Script Selection: Use User-Reviewed Custom Script if provided, else generate
    if custom_script and isinstance(custom_script, dict) and custom_script.get("hook"):
        print(f"  -> Using User-Reviewed & Approved Roman Urdu Script!")
        script_data = custom_script
    else:
        print(f"  -> Generating high-converting Roman Urdu script...")
        from backend.modules.roman_urdu_script import generate_roman_urdu_script
        script_data = generate_roman_urdu_script(
            product_name=product_prompt,
            category=category,
            target_gender=target_gender,
            target_duration=target_duration
        )
    
    # 2. Compliance Check
    print("  -> Checking compliance against banned claims...")
    qc_result = check_compliance(script_data)
    
    # 3. Audio Voiceover
    print(f"  -> Synthesizing authentic speech with voice: {voice_key}...")
    voiceover_parts = [script_data.get("hook", "")]
    for scene in script_data.get("scenes", []):
        voiceover_parts.append(scene.get("voiceover", ""))
    full_voice_text = " ".join(voiceover_parts)
    
    audio_path = os.path.join(r"F:\Projects\beauty-marketing-agent\storage\audio", f"{item_id}.mp3")
    generate_voiceover(full_voice_text, voice_key=voice_key, output_path=audio_path)
    
    # 4. Multi-Scene Visuals (4 Distinct 1080x1920 Luxury Scene Cards)
    print("  -> Generating 4-Scene 1080x1920 visual cards (Hook, Formula, Demo, CTA)...")
    theme = "mens" if target_gender.lower() == "men" else "rose_sunset"
    raw_dir = r"F:\Projects\beauty-marketing-agent\storage\raw_assets"
    
    scene_cards = create_multi_scene_cards(
        script_data=script_data,
        output_dir=raw_dir,
        item_id=item_id,
        theme=theme,
        product_image_path=product_image_path
    )
    
    scenes = script_data.get("scenes", [])
    # Clean card hook: use English/Roman subtitle or on_screen_text so graphics never show unshaped Urdu glyphs
    card_hook = ""
    if scenes and len(scenes) > 0:
        card_hook = scenes[0].get("subtitle") or scenes[0].get("on_screen_text", "")
    if not card_hook:
        card_hook = script_data.get("narrative_angle", "Authentic Formula & Glow Routine")
        
    demo_sub = ""
    if len(scenes) > 2:
        demo_sub = scenes[2].get("subtitle") or scenes[2].get("on_screen_text", "")
    elif len(scenes) > 0:
        demo_sub = scenes[0].get("subtitle") or scenes[0].get("on_screen_text", "")
    if not demo_sub:
        demo_sub = "Tap link in bio to shop original batch!"
    
    real_action_type = script_data.get("action_type") or action_type
    
    ACTION_LABELS = {
        "handwash_cleanse": "Liquid Hand Wash & 20s Cleanse",
        "bodywash_cleanse": "Body Wash & Shower Foam Lather",
        "sanitizer_rub": "Hand Sanitizer & Instant Clean",
        "facewash_cleanse": "Face Wash Cleanse & Foam Lather",
        "face_application": "Serum Dropper & Glass Skin Glow",
        "sunscreen_apply": "UV Shield & Two-Finger Application",
        "cream_massage": "Moisturizer Barrier Massage",
        "lotion_spread": "Body Hydration & Velvety Spread",
        "balm_application": "Fingertip Balm & Lip Moisture Lock",
        "soap_lather": "Creamy Bath Lather & Cleanse",
        "hair_application": "Scalp Massage & Hair Nourishment",
        "fashion_walk": "Dress Drape & Tailored Fit Walk",
        "beard_grooming": "Beard Grooming & Sharp Jawline"
    }
    action_disp_label = ACTION_LABELS.get(real_action_type, real_action_type.replace("_", " ").title())
    
    # Also save master thumbnail card
    card_path = os.path.join(raw_dir, f"{item_id}_card.jpg")
    create_aesthetic_card(
        title=product_prompt,
        subtitle=card_hook,
        action_text=action_disp_label,
        active_subtitle_text=demo_sub,
        output_path=card_path,
        theme=theme,
        product_image_path=product_image_path
    )
    
    # 5. FFmpeg Multi-Scene Animated Video Render with Smooth Transitions, BGM & Avatar
    print(f"  -> Rendering multi-scene 1080x1920 MP4 vertical video with FFmpeg (BGM: {bgm_track}, Avatar: {avatar_character})...")
    video_path = os.path.join(r"F:\Projects\beauty-marketing-agent\storage\output_videos", f"{item_id}.mp4")
    
    talking_avatar_used = False
    ai_video_source = None
    
    # 5a0. Real Cloud AI Video Generator (Kling 1.6 / Minimax / Wan 2.1 via Replicate or Fal)
    if (video_engine_provider in ["replicate", "fal", "hedra"] and video_engine_key) or os.environ.get("REPLICATE_API_TOKEN"):
        try:
            from backend.modules.ai_video_generator import generate_ai_video
            ai_prompt = f"Cinematic 4k commercial video of Pakistani beauty model smiling, lathering and demonstrating {product_prompt} with rich creamy foam, pristine studio lighting."
            v_res = generate_ai_video(
                prompt=ai_prompt,
                image_path=product_image_path or (scene_cards[0] if scene_cards else None),
                provider=video_engine_provider or "replicate",
                model=video_engine_model or "kling",
                api_key=video_engine_key or os.environ.get("REPLICATE_API_TOKEN"),
                duration=5,
                aspect_ratio="9:16"
            )
            if v_res.get("status") == "success" and os.path.exists(v_res.get("video_path")):
                print(f"[AIVideoGenerator] Generated real AI motion video via {video_engine_provider}: {v_res['video_path']}")
                ai_video_source = v_res.get("video_path")
        except Exception as e:
            print(f"[AIVideoGenerator] Exception: {e}")

    # 5a. 3D Supermodel Motion Engine (High-Fashion / Cinematic Priority)
    from backend.modules.supermodel_engine import SUPERMODELS, render_supermodel_cinematic_reel
    active_supermodel = supermodel_id or (avatar_character if avatar_character in SUPERMODELS else None)
    
    if active_supermodel and active_supermodel in SUPERMODELS:
        try:
            print(f"  -> Rendering 3D Supermodel Reel for {active_supermodel} (Hair: {hairstyle}, Wardrobe: {wardrobe})...")
            render_supermodel_cinematic_reel(
                supermodel_id=active_supermodel,
                audio_path=audio_path,
                output_video_path=video_path,
                product_name=product_prompt,
                hook_text=script_data.get("hook", card_hook),
                product_image_path=product_image_path,
                hairstyle=hairstyle or "Natural Waves",
                wardrobe=wardrobe or "Standard",
                target_duration=target_duration,
                source_video_override=ai_video_source
            )
            if os.path.exists(video_path) and os.path.getsize(video_path) > 1000:
                talking_avatar_used = True
                print(f"[SupermodelEngine] Successfully rendered cinematic reel: {video_path}")
        except Exception as e:
            print(f"[SupermodelEngine] Render exception: {e}")

    # 5b. Fallback to D-ID / HeyGen if Supermodel not used and external key provided
    if not talking_avatar_used:
        if not heygen_api_key:
            heygen_api_key = os.environ.get("DID_API_KEY") or os.environ.get("HEYGEN_API_KEY")

        if heygen_api_key and avatar_character != "none":
            from backend.modules.avatar_engine import get_avatar_image_path
            photo_p = get_avatar_image_path(avatar_character)
            
            # Check if D-ID API key (contains ':' or length < 55)
            if ":" in heygen_api_key or len(heygen_api_key) < 55:
                try:
                    from backend.modules.did_engine import generate_did_talking_avatar
                    print(f"  -> Calling D-ID Talking Avatar API with character {avatar_character}...")
                    d_res = generate_did_talking_avatar(
                        api_key=heygen_api_key,
                        character_photo_path=photo_p,
                        script_text=full_voice_text,
                        voice_key=voice_key,
                        audio_path=audio_path,
                        output_video_path=video_path,
                        avatar_character=avatar_character,
                        product_name=product_prompt,
                        hook_text=script_data.get("hook", "")
                    )
                    if d_res.get("status") == "success":
                        talking_avatar_used = True
                        print(f"[D-ID] Successfully generated talking avatar video: {video_path}")
                    else:
                        print(f"[D-ID] Error: {d_res.get('message')}")
                except Exception as e:
                    print(f"[D-ID] Exception: {e}")
                    
            # If D-ID not used or failed, try HeyGen
            if not talking_avatar_used:
                try:
                    from backend.modules.heygen_engine import generate_heygen_talking_avatar
                    print(f"  -> Calling HeyGen Deep-Sync Talking Avatar API...")
                    h_res = generate_heygen_talking_avatar(
                        api_key=heygen_api_key,
                        character_photo_path=photo_p,
                        script_text=full_voice_text,
                        audio_path=audio_path,
                        output_video_path=video_path
                    )
                    if h_res.get("status") == "success":
                        talking_avatar_used = True
                        print(f"[HeyGen] Successfully rendered deep-sync talking avatar video: {video_path}")
                    else:
                        print(f"[HeyGen] Fallback: {h_res.get('message')}")
                except Exception as e:
                    print(f"[HeyGen] Exception: {e}")
            
    if not talking_avatar_used:
        render_multi_scene_video(
            scene_cards, 
            audio_path, 
            video_path, 
            bgm_key=bgm_track,
            avatar_character=avatar_character,
            avatar_layout=avatar_layout,
            script_hook=card_hook,
            product_title=product_prompt,
            script_data=script_data,
            product_image_path=product_image_path
        )
    
    # 6. Export Pack Staging
    print("  -> Packaging into export pack (.zip)...")
    pack_path = create_export_pack(item_id, video_path, script_data)
    
    voice_name = AVAILABLE_VOICES.get(voice_key, {}).get("name", voice_key)
    
    record = {
        "id": item_id,
        "product_name": product_prompt,
        "category": category,
        "target_gender": target_gender,
        "language": language,
        "voice_key": voice_key,
        "voice_name": voice_name,
        "bgm_track": bgm_track,
        "avatar_character": avatar_character,
        "supermodel_id": active_supermodel,
        "hairstyle": hairstyle or "Natural",
        "wardrobe": wardrobe or "Standard",
        "avatar_layout": avatar_layout,
        "action_type": real_action_type,
        "target_duration": target_duration,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "In Review",
        "script": script_data,
        "qc": qc_result,
        "video_path": video_path,
        "audio_path": audio_path,
        "card_path": card_path,
        "scene_cards": scene_cards,
        "pack_path": pack_path,
        "product_image_path": product_image_path,
        "views": 0,
        "likes": 0,
        "clicks": 0
    }
    
    db = _load_db()
    db.insert(0, record)
    _save_db(db)
    
    print(f"[OK] Pipeline complete! Full video saved: {video_path}")
    return record

if __name__ == "__main__":
    res = run_pipeline(
        product_prompt="Garnier Bright Complete Vitamin C Serum",
        category="beauty_skincare",
        target_gender="women",
        language="urdu",
        action_type="face_application",
        voice_key="uzma_pk",
        target_duration=30
    )
    print("Rendered pure Urdu video:", res["id"])
