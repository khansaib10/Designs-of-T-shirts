import os
import json
import random
import string
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── Configuration ─────────────────────────────────────────────────────────────
DRIVE_FOLDER_ID    = os.getenv("DRIVE_FOLDER_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
if not DRIVE_FOLDER_ID or not GOOGLE_CREDENTIALS:
    raise Exception("Please set DRIVE_FOLDER_ID and GOOGLE_CREDENTIALS env vars.")

# Premium fonts (must be in repo)
FONTS = [
    "CalSans-Regular.ttf",
    "RobotoMono-VariableFont_wght.ttf",
    "Tagesschrift-Regular.ttf"
]

# Color palettes (hex strings)
PALETTES = [
    ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
    ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087"],
    ["#0b3954", "#bfd7ea", "#ff6663", "#e0ff4f", "#50514f"]
]
# ────────────────────────────────────────────────────────────────────────────────

def generate_gradient(size, colors):
    """Create a vertical gradient spanning the given color stops."""
    W, H = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    stops = len(colors) - 1

    for y in range(H):
        pos = (y / (H - 1)) * stops
        idx = int(pos)
        # clamp idx
        if idx >= stops:
            idx = stops - 1
            t = 1.0
        else:
            t = pos - idx

        # parse hex to RGB
        def hex_to_rgb(h): return tuple(int(h[i:i+2], 16) for i in (1,3,5))
        c1 = hex_to_rgb(colors[idx])
        c2 = hex_to_rgb(colors[idx+1])

        # interpolate
        r = int(c1[0]*(1-t) + c2[0]*t)
        g = int(c1[1]*(1-t) + c2[1]*t)
        b = int(c1[2]*(1-t) + c2[2]*t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    return img

def draw_shapes(img):
    draw = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    for _ in range(random.randint(5, 10)):
        shape = random.choice(["circle", "rectangle", "triangle"])
        color = random.choice([(255,255,255,80), (0,0,0,50)])
        if shape == "circle":
            r = random.randint(50, 150)
            x, y = random.randint(-r, W), random.randint(-r, H)
            draw.ellipse((x, y, x+r, y+r), fill=color)
        elif shape == "rectangle":
            w, h = random.randint(100, 300), random.randint(50, 200)
            x, y = random.randint(-w, W), random.randint(-h, H)
            draw.rectangle((x, y, x+w, y+h), fill=color)
        else:  # triangle
            pts = [(random.randint(0, W), random.randint(0, H)) for _ in range(3)]
            draw.polygon(pts, fill=color)
    return img

def overlay_text(img, text):
    draw = ImageDraw.Draw(img)
    W, H = img.size
    font_path = random.choice(FONTS) if FONTS else None
    font_size = int(W * 0.1)
    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    # measure text
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x, y = (W-tw)/2, (H-th)/2
    # drop shadow
    for dx, dy in [(-2,-2),(2,-2),(2,2),(-2,2)]:
        draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0,180))
    draw.text((x, y), text, font=font, fill=(255,255,255,255))
    return img

def upload_to_drive(filepath):
    creds_info = json.loads(GOOGLE_CREDENTIALS)
    creds = service_account.Credentials.from_service_account_info(
        creds_info, scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": os.path.basename(filepath), "parents": [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(filepath, mimetype="image/png")
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ Uploaded {filepath}")

def main():
    size = (1024, 1024)
    palette = random.choice(PALETTES)
    img = generate_gradient(size, palette)
    img = draw_shapes(img)
    slogan = random.choice(["Dream Big","Stay Wild","Good Vibes","Be Yourself","Adventure Awaits"])
    img = overlay_text(img, slogan)
    filename = f"design_{''.join(random.choices(string.ascii_lowercase+string.digits, k=6))}.png"
    img.save(filename)
    print(f"💾 Saved {filename}")
    upload_to_drive(filename)

if __name__ == "__main__":
    main()
