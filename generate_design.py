import os
import json
import random
import string
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load Huggingface token
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Load Google Drive credentials from environment variable
credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/drive.file"]
)

# Initialize Google Drive service
drive_service = build('drive', 'v3', credentials=credentials)

# Function to generate AI background
def generate_ai_background():
    print("Generating AI Background...")
    api_url = "https://api-inference.huggingface.co/models/prompthero/openjourney"  # changed model here
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": "fantasy colorful landscape, vibrant background, high quality",
        "options": {
            "wait_for_model": True
        }
    }
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"AI generation failed: {response.text}")

    return Image.open(BytesIO(response.content))

# Function to generate random text
def generate_random_text():
    words = ["Dream", "Inspire", "Create", "Adventure", "Freedom", "Explore", "Believe", "Imagine"]
    return random.choice(words) + " " + random.choice(words)

# Function to overlay text on the background
def create_design(background, text):
    print("Adding text to design...")
    draw = ImageDraw.Draw(background)
    font_size = int(background.size[1] * 0.1)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(text, font=font)
    position = ((background.size[0] - text_width) // 2, (background.size[1] - text_height) // 2)

    draw.text(position, text, font=font, fill=(255, 255, 255))
    return background

# Function to upload to Google Drive
def upload_to_drive(file_path, filename):
    print("Uploading to Google Drive...")
    file_metadata = {"name": filename}
    media = MediaFileUpload(file_path, mimetype='image/png')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded file ID: {file.get('id')}")

# Main function
def main():
    bg = generate_ai_background()
    text = generate_random_text()
    design = create_design(bg, text)

    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + ".png"
    filepath = f"/tmp/{filename}"
    design.save(filepath)

    upload_to_drive(filepath, filename)

if __name__ == "__main__":
    main()
