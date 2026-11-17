import os
import shutil
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MUSIC_DIR = os.path.join(PROJECT_ROOT, "storage", "music")

AVAILABLE_BGM_TRACKS = {
    "lofi_chill": {
        "id": "lofi_chill",
        "name": "Lo-Fi Skincare Routine (Calm Chill)",
        "mood": "Relaxed & Minimalist",
        "filename": "lofi_chill.mp3"
    },
    "luxury_lounge": {
        "id": "luxury_lounge",
        "name": "Luxury Boutique Ambient (Deep Warmth)",
        "mood": "High-End & Aesthetic",
        "filename": "luxury_lounge.mp3"
    },
    "acoustic_warm": {
        "id": "acoustic_warm",
        "name": "Organic Warm Acoustic (Friendly & Upbeat)",
        "mood": "Natural & Approachable",
        "filename": "acoustic_warm.mp3"
    },
    "none": {
        "id": "none",
        "name": "None (Pure Authentic Voiceover Only)",
        "mood": "Studio Silence",
        "filename": None
    }
}

def get_bgm_list() -> list:
    return list(AVAILABLE_BGM_TRACKS.values())

def find_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if path:
        return path
    custom_path = r"C:\Users\Shahid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
    if os.path.exists(custom_path):
        return custom_path
    raise RuntimeError("FFmpeg executable not found!")

def find_ffprobe() -> str:
    path = shutil.which("ffprobe")
    if path:
        return path
    custom_path = r"C:\Users\Shahid\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffprobe.exe"
    if os.path.exists(custom_path):
        return custom_path
    return "ffprobe"

def get_audio_duration(audio_path: str) -> float:
    ffprobe_bin = find_ffprobe()
    cmd = [
        ffprobe_bin,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        val = float(res.stdout.strip())
        if val > 0:
            return val
    except Exception:
        pass
    return 30.0

def render_vertical_video(
    image_path: str, 
    audio_path: str, 
    output_path: str, 
    bgm_key: str = "lofi_chill"
) -> str:
    """
    Renders a vertical 1080x1920 MP4 video combining image/card with voiceover audio
    and optional royalty-free background music with auto-ducking (-filter_complex amix).
    """
    ffmpeg_bin = find_ffmpeg()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    bgm_info = AVAILABLE_BGM_TRACKS.get(bgm_key, AVAILABLE_BGM_TRACKS["lofi_chill"])
    bgm_filename = bgm_info.get("filename")
    bgm_path = os.path.join(MUSIC_DIR, bgm_filename) if bgm_filename else None
    
    # If BGM is requested and file exists on disk, mix with auto-ducking (voice at 100%, BGM at 14%)
    if bgm_path and os.path.exists(bgm_path):
        cmd = [
            ffmpeg_bin,
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-stream_loop", "-1",
            "-i", bgm_path,
            "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.14[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920",
            "-shortest",
            output_path
        ]
    else:
        # Voiceover only
        cmd = [
            ffmpeg_bin,
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920",
            "-shortest",
            output_path
        ]
        
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg render failed: {result.stderr}")
        
    return output_path


from backend.modules.avatar_engine import (
    AVATAR_PRESETS,
    get_avatar_image_path,
    generate_pip_talking_loop,
    generate_split_presenter_card,
    generate_fullscreen_presenter_card
)
from backend.modules.multi_angle_engine import (
    CAMERA_ANGLES,
    get_creator_footage_clip,
    generate_multi_angle_scene_cards,
    generate_transparent_scene_overlays
)

def render_multi_scene_video(
    scene_image_paths: list, 
    audio_path: str, 
    output_path: str, 
    bgm_key: str = "lofi_chill",
    transition_duration: float = 0.45,
    avatar_character: str = "none",
    avatar_layout: str = "intro_outro",
    script_hook: str = None,
    product_title: str = None,
    script_data: dict = None,
    product_image_path: str = None
) -> str:
    """
    Renders an animated multi-scene vertical 1080x1920 MP4 video combining distinct camera angles,
    dynamic cinematic camera motions (push-in, 45° slider pan, macro focus, wide punch),
    synchronized spoken voiceover audio, and background music with auto-ducking.
    """
    ffmpeg_bin = find_ffmpeg()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    active_scenes = list(scene_image_paths) if scene_image_paths else []
    overlays_to_use = []
    
    # Handle Dynamic Multi-Angle Creator System (Default when any avatar is chosen)
    if avatar_character != "none" and avatar_character in AVATAR_PRESETS:
        temp_dir = os.path.join(os.path.dirname(output_path), "multi_angle_temp")
        os.makedirs(temp_dir, exist_ok=True)
        item_prefix = os.path.basename(output_path).replace(".mp4", "")
        
        # Check if real custom MP4 video footage clips exist in storage/creator_footage/{avatar_id}/
        real_clips = []
        for i in range(1, 5):
            clip = get_creator_footage_clip(avatar_character, i)
            if clip:
                real_clips.append(clip)
                
        if len(real_clips) == 4:
            active_scenes = real_clips
            s_data = script_data or {"hook": script_hook, "scenes": []}
            overlays_to_use = generate_transparent_scene_overlays(
                avatar_id=avatar_character,
                output_dir=temp_dir,
                item_id=item_prefix,
                script_data=s_data,
                product_title=product_title
            )
            print(f"  -> [Multi-Angle Engine] Using 4 REAL MP4 video clips with dynamic subtitle overlays for {avatar_character}!")
        else:
            # Generate 4 distinct camera angle cards
            s_data = script_data or {"hook": script_hook, "scenes": []}
            multi_cards = generate_multi_angle_scene_cards(
                avatar_id=avatar_character,
                output_dir=temp_dir,
                item_id=item_prefix,
                script_data=s_data,
                product_image_path=product_image_path
            )
            active_scenes = multi_cards
            print(f"  -> [Multi-Angle Engine] Generated 4 distinct camera angles (Front Hook, 45° Side, Macro Demo, Wide CTA)")

    if not active_scenes or len(active_scenes) == 1:
        single_img = active_scenes[0] if active_scenes else ""
        return render_vertical_video(single_img, audio_path, output_path, bgm_key=bgm_key)
    
    total_duration = get_audio_duration(audio_path)
    N = len(active_scenes)
    t = min(transition_duration, (total_duration / N) * 0.4)
    d_clip = (total_duration + (N - 1) * t) / N
    
    bgm_info = AVAILABLE_BGM_TRACKS.get(bgm_key, AVAILABLE_BGM_TRACKS["lofi_chill"])
    bgm_filename = bgm_info.get("filename")
    bgm_path = os.path.join(MUSIC_DIR, bgm_filename) if bgm_filename else None
    has_bgm = bool(bgm_path and os.path.exists(bgm_path))

    # Build input arguments
    cmd = [ffmpeg_bin, "-y"]
    for src_p in active_scenes:
        if src_p.endswith(".mp4") or src_p.endswith(".mov"):
            cmd.extend(["-stream_loop", "-1", "-t", f"{d_clip:.3f}", "-i", src_p])
        else:
            cmd.extend(["-loop", "1", "-t", f"{d_clip:.3f}", "-i", src_p])

    if overlays_to_use and len(overlays_to_use) == N:
        for ov_p in overlays_to_use:
            cmd.extend(["-loop", "1", "-t", f"{d_clip:.3f}", "-i", ov_p])
        audio_idx = 2 * N
    else:
        overlays_to_use = []
        audio_idx = N
        
    cmd.extend(["-i", audio_path])
    
    next_input_idx = audio_idx + 1
    bgm_idx = None
    if has_bgm:
        cmd.extend(["-stream_loop", "-1", "-i", bgm_path])
        bgm_idx = next_input_idx
        next_input_idx += 1

    # Dynamic Multi-Camera Motion Filters for each angle:
    # Angle 0 (Front Hook): Cinematic push-in
    # Angle 1 (Side Analysis): 45-degree horizontal camera slider drift
    # Angle 2 (Macro Demo): Tight macro focus zoom
    # Angle 3 (CTA Hero): Dynamic wide punch
    angle_filters = [
        "zoompan=z='min(zoom+0.0008,1.06)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,fps=25,setsar=1",
        "zoompan=z='1.04':d=125:x='if(lte(on,1),0,min(x+0.4,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':s=1080x1920,fps=25,setsar=1",
        "zoompan=z='min(zoom+0.0010,1.07)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,fps=25,setsar=1",
        "zoompan=z='max(1.05-0.0006*on,1.00)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,fps=25,setsar=1"
    ]

    filter_parts = []
    for i in range(N):
        src_p = active_scenes[i]
        if src_p.endswith(".mp4") or src_p.endswith(".mov"):
            if overlays_to_use:
                filter_parts.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25,settb=AVTB,setsar=1[base{i}];")
                filter_parts.append(f"[base{i}][{N + i}:v]overlay=0:0:shortest=1[v{i}];")
            else:
                filter_parts.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25,settb=AVTB,setsar=1[v{i}];")
        else:
            motion_filter = angle_filters[i % len(angle_filters)]
            filter_parts.append(f"[{i}:v]{motion_filter}[v{i}];")
        
    prev_label = "[v0]"
    current_offset = d_clip - t
    for i in range(1, N):
        out_label = f"[x{i}]" if i < N - 1 else "[vout]"
        filter_parts.append(f"{prev_label}[v{i}]xfade=transition=fade:duration={t:.3f}:offset={current_offset:.3f}{out_label};")
        prev_label = out_label
        current_offset += (d_clip - t)

    # Audio mixing
    if has_bgm and bgm_idx is not None:
        filter_parts.append(f"[{audio_idx}:a]volume=1.0[voice];[{bgm_idx}:a]volume=0.14[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]")
        filter_complex = "".join(filter_parts)
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]"
        ])
    else:
        filter_complex = "".join(filter_parts)
        if filter_complex.endswith(";"):
            filter_complex = filter_complex[:-1]
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", f"{audio_idx}:a"
        ])
        
    cmd.extend([
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ])
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg multi-scene render failed: {result.stderr}")
        
    return output_path

if __name__ == "__main__":
    img = r"F:\Projects\beauty-marketing-agent\storage\raw_assets\test_rose_card.jpg"
    aud = r"F:\Projects\beauty-marketing-agent\storage\audio\preview_uzma_pk.mp3"
    out = r"F:\Projects\beauty-marketing-agent\storage\output_videos\test_render_music.mp4"
    if os.path.exists(img) and os.path.exists(aud):
        render_vertical_video(img, aud, out, bgm_key="lofi_chill")
        print(f"Rendered video with BGM: {out}")
