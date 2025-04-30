import os
import random
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Settings
WIDTH = 1024
HEIGHT = 1024
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 60
QUOTE_API = "https://api.quotable.io/random?maxLength=50"

# Google Drive
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
if not DRIVE_FOLDER_ID:
    raise Exception("DRIVE_FOLDER_ID is missing in environment variables.")

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    return service

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
    service = get_drive_service()
    file_metadata = {
        'name': file_name,
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype='image/png')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
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

    os.remove(file_path)
    print(f"🧹 Local file {file_name} deleted.")

if __name__ == "__main__":
    main()
