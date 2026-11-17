import subprocess
import os

paths = [
    os.path.abspath(f'storage/test_scenes/s_{i+1}.jpg') for i in range(4)
]
out_vid = os.path.abspath('storage/test_scenes/test_xfade.mp4')
audio_path = os.path.abspath('test_uzma.mp3')

# Duration per clip = 1.3s, transition = 0.3s
# offset1 = 1.0s, offset2 = 2.0s, offset3 = 3.0s -> total video = 4.0s
filter_complex = (
    "[0:v]scale=1080:1920,setsar=1[v0];"
    "[1:v]scale=1080:1920,setsar=1[v1];"
    "[2:v]scale=1080:1920,setsar=1[v2];"
    "[3:v]scale=1080:1920,setsar=1[v3];"
    "[v0][v1]xfade=transition=fade:duration=0.3:offset=1.0[x1];"
    "[x1][v2]xfade=transition=fade:duration=0.3:offset=2.0[x2];"
    "[x2][v3]xfade=transition=fade:duration=0.3:offset=3.0[v]"
)

cmd = [
    'ffmpeg', '-y',
    '-loop', '1', '-t', '1.3', '-i', paths[0],
    '-loop', '1', '-t', '1.3', '-i', paths[1],
    '-loop', '1', '-t', '1.3', '-i', paths[2],
    '-loop', '1', '-t', '1.3', '-i', paths[3],
    '-i', audio_path,
    '-filter_complex', filter_complex,
    '-map', '[v]',
    '-map', '4:a',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-shortest',
    out_vid
]

res = subprocess.run(cmd, capture_output=True, text=True)
print('xfade returncode:', res.returncode)
if res.returncode == 0:
    print('xfade Success! File size:', os.path.getsize(out_vid))
else:
    print('Error:', res.stderr[-500:])
