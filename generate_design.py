import os
import time
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Config
QUOTE_API        = "https://api.quotable.io/random?maxLength=100"
PIXABAY_API_KEY  = "50023073-76bc3ff20218626ffd04d9237"
IMG_SIZE         = (1024, 1024)
TEXT_COLOR       = (0, 0, 0)  # Black text now (for visibility)
FONT_PATH        = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE        = 48
MAX_LINE_WIDTH   = 30

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
    query = "animal"  # You can change this to 'abstract', 'nature', etc
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=vector&colors=transparent&per_page=50"
    
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()

    if not data["hits"]:
        raise Exception("No images found.")

    # Pick a random image
    import random
    img_url = random.choice(data["hits"])["largeImageURL"]

    # Download image
    img_resp = requests.get(img_url, timeout=10)
    img_resp.raise_for_status()

    return Image.open(BytesIO(img_resp.content)).convert("RGBA")

def create_quote_image(quote):
    try:
        base_img = download_random_png()
        base_img = base_img.resize(IMG_SIZE)
    except Exception as e:
        print("Failed to download PNG, fallback to blank image:", e)
        base_img = Image.new("RGBA", IMG_SIZE, (255, 255, 255, 0))

    draw = ImageDraw.Draw(base_img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        font = ImageFont.load_default()

    # wrap text
    lines = textwrap.wrap(quote, width=MAX_LINE_WIDTH)
    total_height = len(lines) * (FONT_SIZE + 10)
    y = IMG_SIZE[1] - total_height - 50  # 50px above bottom

    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:]
        x = (IMG_SIZE[0] - w) / 2
        draw.text((x, y), line, fill=TEXT_COLOR, font=font)
        y += FONT_SIZE + 10

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

    img = create_quote_image(quote)

    filename = f"quote_{int(time.time())}.png"
    img.save(filename)
    print("Saved image:", filename)

    file_id = upload_to_drive(filename, filename)
    print("Uploaded to Drive, file ID =", file_id)

    os.remove(filename)

if __name__ == "__main__":
    main()
