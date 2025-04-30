import os
import time
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Config
QUOTE_API        = "https://api.quotable.io/random?maxLength=100"
IMG_SIZE         = (1024, 1024)
BG_COLOR         = (255, 255, 255, 0)  # Transparent background (RGBA)
TEXT_COLOR       = (255, 255, 255)      # White text
FONT_PATH        = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE        = 48
MAX_LINE_WIDTH   = 30                   # chars per wrapped line

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

def create_quote_image(quote):
    # Create image with a transparent background
    img = Image.new("RGBA", IMG_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        font = ImageFont.load_default()

    # wrap text into lines
    lines = textwrap.wrap(quote, width=MAX_LINE_WIDTH)
    total_height = len(lines) * (FONT_SIZE + 10)
    y = (IMG_SIZE[1] - total_height) / 2

    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:]  # For width and height of text
        x = (IMG_SIZE[0] - w) / 2
        draw.text((x, y), line, fill=TEXT_COLOR, font=font)
        y += FONT_SIZE + 10

    return img

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

    # Use time.time() instead of textwrap.time
    filename = f"quote_{int(time.time())}.png"
    img.save(filename, format="PNG", quality=100)  # Ensure high quality for printing
    print("Saved image:", filename)

    file_id = upload_to_drive(filename, filename)
    print("Uploaded to Drive, file ID =", file_id)

    os.remove(filename)

if __name__ == "__main__":
    main()
