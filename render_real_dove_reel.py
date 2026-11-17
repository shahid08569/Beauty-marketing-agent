import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

def render():
    c1 = r'storage\raw_assets\c1.mp4'
    c2 = r'storage\raw_assets\c2.mp4'
    c3 = r'storage\raw_assets\c3.mp4'
    audio = r'storage\raw_assets\test_dove_voiceover.mp3'
    bgm = r'storage\music\lofi_chill.mp3'
    out = r'storage\output_videos\dove_soap_official_commercial.mp4'

    # Create overlay card
    overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    try:
        f_pill = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 24)
        f_title = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 40)
        f_sub = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 24)
        f_cta = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 24)
    except Exception:
        f_pill = f_title = f_sub = f_cta = ImageFont.load_default()

    # Top Verified Pill
    d.rounded_rectangle([(40, 60), (1040, 130)], radius=28, fill=(15, 15, 18, 220), outline=(255, 255, 255, 80), width=1)
    d.ellipse([(70, 84), (92, 106)], fill=(16, 185, 129, 255))
    d.text((110, 78), 'DOVE BEAUTY • 1/4 MOISTURIZING CREAM • 100% ORIGINAL', font=f_pill, fill=(247, 245, 240, 255))

    # Bottom Branded Card
    by = 1380
    d.rounded_rectangle([(40, by), (1040, by + 480)], radius=36, fill=(12, 14, 18, 230), outline=(255, 255, 255, 70), width=1)
    d.text((80, by + 45), 'Dove Beauty Cream Bar', font=f_title, fill=(247, 245, 240, 255))
    d.text((80, by + 105), 'Soft, Radiant & Deeply Hydrated Glass-Skin', font=f_sub, fill=(16, 185, 129, 255))
    d.line([(80, by + 155), (1000, by + 155)], fill=(255, 255, 255, 40), width=1)
    d.text((80, by + 185), '"Agar skin dry lagti hai, to Dove ka secret dekhein!"', font=f_title, fill=(255, 255, 255, 255))
    d.text((80, by + 260), '24-Hour Deep Hydration • Rich Creamy Foam Lather', font=f_sub, fill=(209, 213, 219, 255))

    # COD Banner
    d.rounded_rectangle([(80, by + 340), (1000, by + 430)], radius=22, fill=(16, 185, 129, 235))
    d.text((120, by + 368), '● 100% VERIFIED AUTHENTIC BATCH • CASH ON DELIVERY PK', font=f_cta, fill=(255, 255, 255, 255))

    overlay_p = r'storage\raw_assets\dove_overlay.png'
    overlay.save(overlay_p, 'PNG')

    # Concat with xfade and audio
    filter_complex = (
        '[0:v][1:v]xfade=transition=fade:duration=0.5:offset=3.5[v12];'
        '[v12][2:v]xfade=transition=fade:duration=0.5:offset=7.0[v123];'
        '[v123][3:v]overlay=0:0[vout];'
        '[4:a]volume=1.0[v_audio];'
        '[5:a]volume=0.15[bgm_audio];'
        '[v_audio][bgm_audio]amix=inputs=2:duration=first[aout]'
    )

    cmd = [
        'ffmpeg', '-y',
        '-i', c1,
        '-i', c2,
        '-i', c3,
        '-i', overlay_p,
        '-i', audio,
        '-i', bgm,
        '-filter_complex', filter_complex,
        '-map', '[vout]',
        '-map', '[aout]',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-crf', '20',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        out
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    print('Returncode:', res.returncode)
    if res.returncode == 0:
        print('SUCCESS! Output file size:', os.path.getsize(out), 'Path:', out)
    else:
        print('ERROR:', res.stderr[-500:])

if __name__ == '__main__':
    render()
