import os
import time
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from io import BytesIO

# Config
PIXABAY_API_KEY = "50023073-76bc3ff20218626ffd04d9237"
QUOTE_API = "https://api.quotable.io/random?maxLength=100"
IMG_SIZE = (1500, 1500)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 48
MAX_LINE_WIDTH = 30
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
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q=&image_type=vector&per_page=50&colors=transparent"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        hits = r.json().get("hits", [])
        if not hits:
            raise Exception("No images found")
        image_url = hits[0]["largeImageURL"].replace("_640", "_1280")
        img_data = requests.get(image_url, timeout=10).content
        return Image.open(BytesIO(img_data)).convert("RGBA")
    except:
        # fallback if API fails
        img = Image.new("RGBA", IMG_SIZE, (255, 255, 255, 0))
        return img

def create_combined_image(quote):
    background = Image.new("RGBA", IMG_SIZE, (255, 255, 255, 0))  # transparent background

    png_img = download_random_png()

    # Scale down the PNG image
    scale_factor = 0.5
    new_size = (int(png_img.width * scale_factor), int(png_img.height * scale_factor))
    png_img = png_img.resize(new_size, Image.LANCZOS)

    # Paste the PNG higher (Y offset up)
    png_x = (IMG_SIZE[0] - png_img.width) // 2
    png_y = (IMG_SIZE[1] - png_img.height) // 3  # move it UP a little

    background.paste(png_img, (png_x, png_y), png_img)

    # Add text below
    draw = ImageDraw.Draw(background)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        font = ImageFont.load_default()

    lines = textwrap.wrap(quote, width=MAX_LINE_WIDTH)
    total_text_height = len(lines) * (FONT_SIZE + 10)
    text_y = png_y + png_img.height + 30  # start a bit below image

    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:]
        text_x = (IMG_SIZE[0] - w) / 2
        draw.text((text_x, text_y), line, fill=(0, 0, 0), font=font)
        text_y += FONT_SIZE + 10

    return background

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

    img = create_combined_image(quote)

    filename = f"quote_{int(time.time())}.png"
    img.save(filename)
    print("Saved image:", filename)

    file_id = upload_to_drive(filename, filename)
    print("Uploaded to Drive, file ID =", file_id)

    os.remove(filename)

if __name__ == "__main__":
    main()
