import os
import random
import string
import requests
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =============== CONFIGURATION ===============

# Get Google Drive credentials from GitHub Secrets
credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/drive.file"]
)

# HuggingFace API setup
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
model_id = "stabilityai/sdxl-lite"  # ✅ Supported model
api_url = f"https://api-inference.huggingface.co/models/{model_id}"

# Folder name where files will be uploaded in Drive
folder_name = "T-shirt Designs"

# ==============================================

def generate_random_text():
    words = [
        "Adventure", "Freedom", "Wild", "Dream", "Courage",
        "Explore", "Inspire", "Create", "Believe", "Passion"
    ]
    return random.choice(words)

def generate_filename():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".png"

def generate_ai_background():
    print("Generating AI Background...")
    headers = {"Authorization": f"Bearer {huggingface_token}"}
    prompt = "artistic colorful t-shirt background design"
    response = requests.post(api_url, headers=headers, json={"inputs": prompt})

    if response.status_code != 200:
        raise Exception(f"AI generation failed: {response.text}")

    image = Image.open(BytesIO(response.content))
    return image

def create_tshirt_design(background):
    print("Creating T-shirt design...")
    width, height = background.size
    draw = ImageDraw.Draw(background)

    font_size = width // 10
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = generate_random_text()
    text_width, text_height = draw.textsize(text, font=font)

    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2

    draw.text((text_x, text_y), text, font=font, fill="white")

    filename = generate_filename()
    background.save(filename)
    return filename

def upload_to_drive(filename):
    print("Uploading to Google Drive...")
    service = build("drive", "v3", credentials=credentials)

    # Check if folder exists
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces="drive").execute()
    items = results.get("files", [])

    if not items:
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        folder = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = folder.get("id")
    else:
        folder_id = items[0]["id"]

    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }
    media = MediaFileUpload(filename, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"Uploaded {filename} successfully!")

def main():
    bg_image = generate_ai_background()
    design_filename = create_tshirt_design(bg_image)
    upload_to_drive(design_filename)
    print("Process completed.")

if __name__ == "__main__":
    main()
