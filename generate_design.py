import os
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Settings
QUOTE_API_URL = "https://api.quotable.io/random?maxLength=80"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # System font path
IMAGE_SIZE = (1024, 1024)
FONT_SIZE = 60
TEXT_COLOR = (255, 255, 255)

def get_random_quote():
    try:
        response = requests.get(QUOTE_API_URL, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f"{data['content']}"
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return random.choice([
            "Dream Big.", "Stay Positive.", "Believe in Yourself.", "Never Give Up.", "Create Your Future."
        ])

def create_design(quote):
    img = Image.new('RGB', IMAGE_SIZE, color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    text_width, text_height = draw.textbbox((0, 0), quote, font=font)[2:]
    position = ((IMAGE_SIZE[0] - text_width) / 2, (IMAGE_SIZE[1] - text_height) / 2)

    draw.text(position, quote, fill=TEXT_COLOR, font=font, align="center")
    return img

def upload_to_drive(file_path, file_name):
    creds = service_account.Credentials.from_service_account_file('service_account.json', scopes=["https://www.googleapis.com/auth/drive"])
    service = build('drive', 'v3', credentials=creds)

    folder_id = os.getenv("DRIVE_FOLDER_ID")
    if not folder_id:
        raise Exception("DRIVE_FOLDER_ID environment variable not found.")

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='image/png')

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"✅ Uploaded to Drive with file ID: {uploaded_file.get('id')}")

def main():
    quote = get_random_quote()
    print(f"🎯 Quote: {quote}")

    img = create_design(quote)
    file_name = f"design_{int(random.random()*10000000)}.png"
    file_path = os.path.join(".", file_name)
    img.save(file_path)

    print(f"🎨 Design saved locally as {file_name}")
    upload_to_drive(file_path, file_name)

if __name__ == "__main__":
    main()
