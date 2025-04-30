import os
import json
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load and validate environment
DRIVE_FOLDER_ID    = os.getenv("DRIVE_FOLDER_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
if not DRIVE_FOLDER_ID or not GOOGLE_CREDENTIALS:
    raise Exception("Please set DRIVE_FOLDER_ID and GOOGLE_CREDENTIALS in env vars.")

# Premium fonts (must be in repo)
FONTS = [
    "CalSans-Regular.ttf",
    "RobotoMono-VariableFont_wght.ttf",
    "Tagesschrift-Regular.ttf"
]

PALETTES = [
    ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
    ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087"],
    ["#0b3954", "#bfd7ea", "#ff6663", "#e0ff4f", "#50514f"]
]

def generate_gradient(size, colors):
    W, H = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    
    # Ensure there are enough colors in the palette
    if len(colors) < 2:
        raise ValueError("The palette must have at least two colors.")
    
    # Generate gradient with multiple color stops
    segments = len(colors) - 1
    for y in range(H):
        seg_pos = (y / (H - 1)) * segments
        i = int(seg_pos)
        t = seg_pos - i
        c1 = tuple(int(colors[i][j:j+2], 16) for j in (1,3,5))
        c2 = tuple(int(colors[i+1][j:j+2], 16) for j in (1,3,5))
        r = int(c1[0]*(1-t) + c2[0]*t)
        g = int(c1[1]*(1-t) + c2[1]*t)
        b = int(c1[2]*(1-t) + c2[2]*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    return img

def draw_shapes(img):
    draw = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    for _ in range(random.randint(5, 10)):
        shape = random.choice(["circle", "rectangle", "triangle"])
        color = random.choice([(255, 255, 255, 80), (0, 0, 0, 50)])
        if shape == "circle":
            r = random.randint(50, 150)
            x = random.randint(-r, W)
            y = random.randint(-r, H)
            draw.ellipse((x, y, x + r, y + r), fill=color)
        elif shape == "rectangle":
            w, h = random.randint(100, 300), random.randint(50, 200)
            x, y = random.randint(-w, W), random.randint(-h, H)
            draw.rectangle((x, y, x + w, y + h), fill=color)
        else:
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
    
    # Use textbbox instead of deprecated textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (W - tw) / 2, (H - th) / 2
    # shadow
    for dx, dy in [(-2, -2), (2, -2), (2, 2), (-2, 2)]:
        draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return img

def upload_to_drive(filepath):
    creds_dict = json.loads(GOOGLE_CREDENTIALS)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": os.path.basename(filepath), "parents": [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(filepath, mimetype="image/png")
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"Uploaded {filepath}")

def main():
    size = (1024, 1024)
    palette = random.choice(PALETTES)
    img = generate_gradient(size, palette)
    img = draw_shapes(img)
    slogan = random.choice(["Dream Big", "Stay Wild", "Good Vibes", "Be Yourself", "Adventure Awaits"])
    img = overlay_text(img, slogan)
    filename = f"design_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}.png"
    img.save(filename)
    print(f"Saved {filename}")
    upload_to_drive(filename)

if __name__ == "__main__":
    main()
