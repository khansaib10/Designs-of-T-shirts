import os
import time
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import random
from io import BytesIO

# Config
QUOTE_API        = "https://api.quotable.io/random?maxLength=100"
IMG_SIZE         = (1024, 1024)
TEXT_COLOR       = (255, 255, 255)     # white text
FONT_PATH        = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE        = 48
MAX_LINE_WIDTH   = 30                  # chars per wrapped line

# Drive setup
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
if not DRIVE_FOLDER_ID:
    raise Exception("Missing DRIVE_FOLDER_ID env var")

PIXABAY_API_KEY = "50023073-76bc3ff20218626ffd04d9237"  # Your Pixabay API Key

def get_random_quote():
    try:
        r = requests.get(QUOTE_API, timeout=10, verify=False)
        r.raise_for_status()
        return r.json()["content"]
    except:
        return "Stay positive and keep moving forward"

def download_random_png(keyword=""):
    try:
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={keyword}&image_type=vector&per_page=50&colors=transparent"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        hits = r.json().get("hits", [])
        if not hits:
            raise Exception("No images found")
        
        # Randomly pick one image from the results
        chosen = random.choice(hits)
        
        image_url = chosen["largeImageURL"].replace("_640", "_1280")
        img_data = requests.get(image_url, timeout=10).content
        return Image.open(BytesIO(img_data)).convert("RGBA")
    
    except Exception as e:
        print(f"Error: {e}. Returning empty image.")
        img = Image.new("RGBA", IMG_SIZE, (255, 255, 255, 0))  # Transparent image
        return img

def create_quote_image(quote, keyword=""):
    img = download_random_png(keyword)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        font = ImageFont.load_default()

    # Wrap text into lines
    lines = textwrap.wrap(quote, width=MAX_LINE_WIDTH)
    total_height = len(lines) * (FONT_SIZE + 10)
    y = (IMG_SIZE[1] - total_height) / 2

    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:]  # Get text width and height
        x = (IMG_SIZE[0] - w) / 2  # Center align text
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

    # Choose a keyword (you can customize or use dynamic input)
    keyword = "dog"  # Example: You can change this to "cat", "adventure", "bike", etc.

    img = create_quote_image(quote, keyword)

    # Save image with timestamped filename
    filename = f"quote_{int(time.time())}.png"
    img.save(filename)
    print("Saved image:", filename)

    # Upload to Google Drive
    file_id = upload_to_drive(filename, filename)
    print("Uploaded to Drive, file ID =", file_id)

    os.remove(filename)

if __name__ == "__main__":
    main()
