import os
import time
import textwrap
import requests
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Config
QUOTE_API = "https://api.quotable.io/random?maxLength=100"
PIXABAY_API_KEY = "50023073-76bc3ff20218626ffd04d9237"
PIXABAY_URL = "https://pixabay.com/api/"
IMG_SIZE = (1200, 1600)
TEXT_COLOR = (0, 0, 0)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 80
MAX_LINE_WIDTH = 22
SEARCH_TERMS = ["dog", "cat", "flower", "mountain", "bike", "tree", "nature", "beach", "bird", "scorpion", "lion", "zebra"]

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

def download_random_png_from_pixabay():
    search_term = random.choice(SEARCH_TERMS)
    params = {
        "key": PIXABAY_API_KEY,
        "q": search_term,
        "image_type": "vector",
        "per_page": 50,
        "safesearch": "true",
        "colors": "transparent"
    }
    r = requests.get(PIXABAY_URL, params=params, timeout=10, verify=False)
    r.raise_for_status()
    data = r.json()

    if not data["hits"]:
        raise Exception(f"No images found for {search_term}")

    chosen = random.choice(data["hits"])
    img_url = chosen["largeImageURL"]

    img_resp = requests.get(img_url, timeout=10, verify=False)
    img_resp.raise_for_status()

    img = Image.open(BytesIO(img_resp.content)).convert("RGBA")
    local_path = f"downloaded_{int(time.time())}.png"
    img.save(local_path)
    print(f"Downloaded PNG for '{search_term}'")
    return local_path

def create_quote_image(png_image_path, quote):
    base_img = Image.new("RGBA", IMG_SIZE, (255, 255, 255, 0))

    png = Image.open(png_image_path).convert("RGBA")
    png_w, png_h = png.size

    max_png_width = IMG_SIZE[0] * 0.8
    if png_w > max_png_width:
        ratio = max_png_width / png_w
        png = png.resize((int(png_w * ratio), int(png_h * ratio)), Image.LANCZOS)
        png_w, png_h = png.size

    x = (IMG_SIZE[0] - png_w) // 2
    base_img.paste(png, (x, 100), png)

    draw = ImageDraw.Draw(base_img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        font = ImageFont.load_default()

    lines = textwrap.wrap(quote, width=MAX_LINE_WIDTH)
    total_text_height = len(lines) * (FONT_SIZE + 10)
    text_start_y = png_h + 150

    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:]
        text_x = (IMG_SIZE[0] - w) / 2
        text_y = text_start_y

        outline_range = 3
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                draw.text((text_x + ox, text_y + oy), line, fill=(255, 255, 255), font=font)

        draw.text((text_x, text_y), line, fill=TEXT_COLOR, font=font)
        text_start_y += FONT_SIZE + 10

    return base_img

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

    png_path = download_random_png_from_pixabay()

    img = create_quote_image(png_path, quote)

    filename = f"quote_{int(time.time())}.png"
    img.save(filename)
    print("Saved image:", filename)

    file_id = upload_to_drive(filename, filename)
    print("Uploaded to Drive, file ID =", file_id)

    os.remove(filename)
    os.remove(png_path)

if __name__ == "__main__":
    main()
