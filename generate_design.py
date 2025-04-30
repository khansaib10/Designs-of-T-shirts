import os
import random
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Authenticate with Google Drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Settings
WIDTH = 1024
HEIGHT = 1024
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # You can change font if you want
FONT_SIZE = 60
QUOTE_API = "https://api.quotable.io/random?maxLength=50"

# Drive Folder ID (Must set in GitHub Actions secrets as DRIVE_FOLDER_ID)
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
if not DRIVE_FOLDER_ID:
    raise Exception("DRIVE_FOLDER_ID is missing in environment variables.")

def fetch_quote():
    """Fetch a random quote."""
    try:
        resp = requests.get(QUOTE_API, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        return f"{data['content']} —{data['author']}"
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return "Stay Positive —Unknown"

def create_text_image(text):
    """Create an image with the given text."""
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    x = (WIDTH - text_width) / 2
    y = (HEIGHT - text_height) / 2

    draw.text((x, y), text, font=font, fill=(0, 0, 0))

    return img

def upload_to_drive(file_path, file_name):
    """Upload a file to Google Drive."""
    file = drive.CreateFile({
        'title': file_name,
        'parents': [{'id': DRIVE_FOLDER_ID}]
    })
    file.SetContentFile(file_path)
    file.Upload()
    print(f"✅ Uploaded {file_name} to Google Drive.")

def main():
    quote = fetch_quote()
    print(f"🎯 Quote: {quote}")

    img = create_text_image(quote)
    file_name = f"design_{int(time.time())}.png"
    file_path = f"./{file_name}"

    img.save(file_path)
    print(f"🎨 Design saved locally as {file_name}")

    upload_to_drive(file_path, file_name)

    # Cleanup
    os.remove(file_path)
    print(f"🧹 Local file {file_name} deleted.")

if __name__ == "__main__":
    main()
