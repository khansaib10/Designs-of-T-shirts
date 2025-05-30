import os
import time
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import random

# Config
QUOTE_API        = "https://api.quotable.io/random?maxLength=100"
PIXABAY_API_KEY  = "50023073-76bc3ff20218626ffd04d9237"
IMG_SIZE = (1200, 1600)  # Bigger canvas
BG_COLOR = (255, 255, 255, 0)  # Transparent
TEXT_COLOR = (0, 0, 0)         # Black text
FONT_SIZE = 56
MAX_LINE_WIDTH = 30
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Add this line

# Drive setup
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
if not DRIVE_FOLDER_ID:
    raise Exception("Missing DRIVE_FOLDER_ID env var")

def get_random_quote():
    try:
        r = requests.get(QUOTE_API, timeout=10, verify=False)
        r.raise_for_status()
        return r.json()["content"]
    except:
        return "Stay positive and keep moving forward"

def download_random_png():
    try:
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&image_type=vector&colors=transparent&per_page=50"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        if not data["hits"]:
            raise Exception("No images found.")

        img_url = random.choice(data["hits"])["largeImageURL"]
        img_resp = requests.get(img_url, timeout=10)
        img_resp.raise_for_status()

        return Image.open(BytesIO(img_resp.content)).convert("RGBA")
    except Exception as e:
        print("Error downloading PNG, fallback blank:", e)
        return Image.new("RGBA", IMG_SIZE, (255, 255, 255, 0))

def create_quote_image(quote):
    # Create blank canvas
    canvas = Image.new("RGBA", IMG_SIZE, (255, 255, 255, 0))

    try:
        base_img = download_random_png()

        # Scale vector smaller
        max_img_width = int(IMG_SIZE[0] * 0.6)  # smaller
        max_img_height = int(IMG_SIZE[1] * 0.5)
        base_img.thumbnail((max_img_width, max_img_height), Image.LANCZOS)

        # Center horizontally, move slightly up
        img_x = (IMG_SIZE[0] - base_img.width) // 2
        img_y = int(IMG_SIZE[1] * 0.1)  # 10% from top
        canvas.paste(base_img, (img_x, img_y), base_img)

    except Exception as e:
        print("Error pasting vector:", e)

    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        font = ImageFont.load_default()

    # Wrap quote
    lines = textwrap.wrap(quote, width=MAX_LINE_WIDTH)
    total_height = len(lines) * (FONT_SIZE + 10)

    # Start quote 70% down
    y = int(IMG_SIZE[1] * 0.7)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (IMG_SIZE[0] - w) / 2

        # Draw outline
        outline_range = 2
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                draw.text((x + ox, y + oy), line, fill=(255, 255, 255), font=font)

        draw.text((x, y), line, fill=TEXT_COLOR, font=font)
        y += FONT_SIZE + 10

    return canvas

def auth_drive():
    creds = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    return build("drive", "v3", credentials=creds)

def upload_to_drive(local_path, name=None):
    service = auth_drive()
    metadata = {
        "name": name or os.path.basename(local_path),
        "parents": [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(local_path, mimetype="image/png")
    file = service.files().create(body=metadata, media_body=media, fields="id").execute()
    return file.get("id")

def main():
    quote = get_random_quote()
    print("Quote:", quote)

    img = create_quote_image(quote)

    filename = f"quote_{int(time.time())}.png"
    img.save(filename)
    print("Saved image:", filename)

    file_id = upload_to_drive(filename, filename)
    print("Uploaded to Drive, file ID =", file_id)

    os.remove(filename)

if __name__ == "__main__":
    main()
