import subprocess
import os
from PIL import Image, ImageDraw

os.makedirs('storage/test_scenes', exist_ok=True)
colors = [(40, 20, 30), (30, 40, 50), (20, 50, 30), (50, 30, 20)]
paths = []
for i, c in enumerate(colors):
    img = Image.new('RGB', (1080, 1920), color=c)
    draw = ImageDraw.Draw(img)
    draw.text((200, 900), f'SCENE {i+1}', fill=(255, 255, 255))
    p = f'storage/test_scenes/s_{i+1}.jpg'
    img.save(p)
    paths.append(os.path.abspath(p))

audio_path = os.path.abspath('test_uzma.mp3')
out_vid = os.path.abspath('storage/test_scenes/test_multi.mp4')
txt_path = os.path.abspath('storage/test_scenes/concat.txt')

with open(txt_path, 'w', encoding='utf-8') as f:
    for p in paths:
        clean_p = p.replace('\\', '/')
        f.write(f"file '{clean_p}'\n")
        f.write("duration 1.08\n")
    clean_p = paths[-1].replace('\\', '/')
    f.write(f"file '{clean_p}'\n")

cmd = [
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0', '-i', txt_path,
    '-i', audio_path,
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-vf', 'scale=1080:1920',
    '-shortest',
    out_vid
]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Concat returncode:', res.returncode)
if res.returncode == 0:
    print('Render successful! Bytes:', os.path.getsize(out_vid))
else:
    print('Stderr:', res.stderr[-500:])
