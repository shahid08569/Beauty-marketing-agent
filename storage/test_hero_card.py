from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

img_p = r"backend\assets\avatars\ayesha_derm.jpg"
out_p = r"storage\test_scenes\test_full_hero_ayesha.jpg"
width, height = 1080, 1920

raw_img = Image.open(img_p).convert("RGBA")

# Canvas
canvas = Image.new("RGBA", (width, height), (19, 19, 20, 255))

# 1. Background: ambient studio blurred glow
bg = raw_img.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=60))
dark_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 130))
bg = Image.alpha_composite(bg, dark_overlay)
canvas.paste(bg, (0, 0))

# 2. Main Presenter Hero: Scaled to fit naturally into upper 70% of frame
pw = 1020
ph = 1020
p_crop = raw_img.resize((pw, ph), Image.Resampling.LANCZOS)

# Soft bottom vignette fade so presenter body fades into the lower third naturally
fade_mask = Image.new("L", (pw, ph), 255)
d_fade = ImageDraw.Draw(fade_mask)
for i in range(250):
    alpha = int(255 * (1.0 - (i / 250.0)))
    d_fade.line([(0, ph - 250 + i), (pw, ph - 250 + i)], fill=alpha)

px = (width - pw) // 2
py = 100
canvas.paste(p_crop, (px, py), fade_mask)

# 3. Broadcast Top Pill
d = ImageDraw.Draw(canvas)
d.rounded_rectangle([(40, 50), (width - 40, 110)], radius=25, fill=(28, 28, 30, 210), outline=(255, 255, 255, 90), width=1)

font_top = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 20)
font_title = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 44)
font_sub = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 24)
font_hook = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 32)

# Live dot
d.ellipse([(65, 72), (85, 92)], fill=(16, 185, 129, 255))
d.text((100, 68), "LIVE CREATOR HOOK • DERMATOLOGIST VERIFIED", font=font_top, fill=(247, 245, 240, 255))

# 4. Luxury Lower Third (Bottom 35%)
by = 1240
bh = 600
d.rounded_rectangle([(40, by), (width - 40, by + bh)], radius=36, fill=(19, 19, 20, 235), outline=(255, 255, 255, 120), width=1)

# Presenter Name & Credentials
d.text((75, by + 45), "Dr. Ayesha Khan", font=font_title, fill=(247, 245, 240, 255))
d.text((75, by + 105), "Senior Consultant Dermatologist • MBBS, FCPS", font=font_sub, fill=(13, 148, 136, 255))

d.line([(75, by + 160), (width - 75, by + 160)], fill=(255, 255, 255, 40), width=1)

# Spoken Hook Subtitle Box
d.text((75, by + 190), "Midday oil, dust, and clogged pores making skin dull?", font=font_hook, fill=(255, 255, 255, 255))
d.text((75, by + 260), "Official Clinical Formula Breakdown & Routine", font=font_sub, fill=(156, 163, 175, 255))

# CTA Seal
d.rounded_rectangle([(75, by + 370), (width - 75, by + 460)], radius=22, fill=(16, 185, 129, 230))
d.text((150, by + 398), "● VERIFIED AUTHENTIC BATCH • CASH ON DELIVERY PK", font=font_top, fill=(255, 255, 255, 255))

canvas.convert("RGB").save(out_p, "JPEG", quality=95)
print("Generated test full hero card:", out_p, "Size:", os.path.getsize(out_p))
