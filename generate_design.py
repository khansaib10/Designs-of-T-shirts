import os
import random
import string
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# Huggingface and Google credentials
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# Model that supports API inference
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

# Random text options for T-shirt designs
DESIGN_TEXTS = [
    "Dream Big", "Stay Wild", "Good Vibes Only", "Adventure Awaits",
    "Born to Ride", "Stay Positive", "Be Yourself", "Never Give Up",
    "Bike Lover", "Ride Free", "Stay Strong", "Love More", "Chase Dreams",
]

def generate_random_text():
    return random.choice(DESIGN_TEXTS)

def generate_ai_background(prompt="A colorful abstract background for T-shirt"):
    print("Generating AI Background...")
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {"inputs": prompt}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"AI generation failed: {response.text}")
    
    image = Image.open(BytesIO(response.content))
    return image

def create_tshirt_design(bg_image, text):
    print("Creating T-shirt Design...")
    # Resize background
    bg_image = bg_image.resize((1024, 1024))
    
    draw = ImageDraw.Draw(bg_image)
    
    try:
        font = ImageFont.truetype("arial.ttf", size=80)
    except:
        font = ImageFont.load_default()
    
    # Text size
    text_width, text_height = draw.textsize(text, font=font)
    position = ((1024 - text_width) / 2, (1024 - text_height) / 2)

    draw.text(position, text, font=font, fill="white")
    return bg_image

def upload_to_drive(file_path, file_name):
    print("Uploading to Google Drive...")
    credentials_info = json.loads(GOOGLE_CREDENTIALS)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {'name': file_name, 'parents': []}
    media = MediaFileUpload(file_path, mimetype='image/png')
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded file ID: {uploaded_file.get('id')}")
    return uploaded_file.get('id')

def save_image_locally(img, folder="designs"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + ".png"
    path = os.path.join(folder, filename)
    img.save(path)
    print(f"Saved image: {path}")
    return path, filename

def main():
    text = generate_random_text()
    bg_image = generate_ai_background()
    final_design = create_tshirt_design(bg_image, text)
    
    path, filename = save_image_locally(final_design)
    
    # Upload to Google Drive
    upload_to_drive(path, filename)

if __name__ == "__main__":
    main()
