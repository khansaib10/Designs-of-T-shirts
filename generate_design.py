import os
import json
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# API details
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
google_credentials = os.getenv("GOOGLE_CREDENTIALS")
api_url = "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo"  # <-- NEW MODEL

def generate_prompt():
    prompts = [
        "Colorful abstract t-shirt design",
        "Futuristic robot t-shirt art",
        "Vintage retro sunset design",
        "Minimalist aesthetic pattern",
        "Fantasy dragon flying in sky",
        "Cute cat with sunglasses",
        "Nature landscape with mountains",
        "Neon cyberpunk cityscape",
        "Japanese anime style character",
        "Psychedelic colorful artwork"
    ]
    return random.choice(prompts)

def generate_ai_background():
    print("Generating AI Background...")
    headers = {
        "Authorization": f"Bearer {huggingface_token}"
    }
    payload = {
        "inputs": generate_prompt()
    }

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"AI generation failed: {response.text}")

    image = Image.open(BytesIO(response.content))
    return image

def create_text_overlay(text, width, height):
    print("Creating text overlay...")
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = random.randint(30, 60)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # common in Linux GitHub runners
    font = ImageFont.truetype(font_path, font_size)

    textwidth, textheight = draw.textsize(text, font=font)
    x = (width - textwidth) / 2
    y = height - textheight - 20

    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    return overlay

def upload_to_drive(filepath):
    print("Uploading to Google Drive...")

    credentials_info = json.loads(google_credentials)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': os.path.basename(filepath),
        'parents': [os.getenv("DRIVE_FOLDER_ID")]
    }
    media = MediaFileUpload(filepath, mimetype='image/png')

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"File uploaded successfully with ID: {uploaded_file['id']}")

def main():
    try:
        bg_image = generate_ai_background()

        text_overlay = create_text_overlay("Limited Edition", bg_image.width, bg_image.height)

        combined = Image.alpha_composite(bg_image.convert('RGBA'), text_overlay)

        filename = f"design_{random.randint(1000, 9999)}.png"
        combined.save(filename, "PNG")
        print(f"Saved {filename}")

        upload_to_drive(filename)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
