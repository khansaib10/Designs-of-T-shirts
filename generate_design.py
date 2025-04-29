import random
import string
from PIL import Image, ImageDraw, ImageFont
import os
import json
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account

# Setup Google Drive API
credentials_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
credentials = service_account.Credentials.from_service_account_info(credentials_info)
service = build('drive', 'v3', credentials=credentials)

# Your Google Drive folder ID
folder_id = '1jnHnezrLNTl3ebmlt2QRBDSQplP_Q4wh'

def create_random_design():
    # Create transparent background
    img = Image.new('RGBA', (1080, 1080), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    # Random motivational words
    words = ['Dream', 'Freedom', 'Hustle', 'Create', 'Inspire', 'Legend', 'Fearless', 'Ambition', 'Grind', 'Passion']
    txt = random.choice(words)

    # Random big font size
    fontsize = random.randint(150, 250)

    # Load font
    try:
        fnt = ImageFont.truetype("arial.ttf", fontsize)
    except:
        fnt = ImageFont.load_default()

    # Calculate text size properly
    bbox = draw.textbbox((0, 0), txt, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # Draw text centered
    draw.text(
        ((1080 - tw) / 2, (1080 - th) / 2),
        txt,
        font=fnt,
        fill=random.choice(['#000000', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'])  # Bright colors
    )

    # Save to memory
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr

# Upload to Google Drive
def upload_to_drive(file_bytes, filename):
    file_metadata = {
        'name': filename,
        'parents': [folder_id],
        'mimeType': 'image/png'
    }
    media = MediaIoBaseUpload(file_bytes, mimetype='image/png')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded file with ID: {file.get('id')}")

if __name__ == "__main__":
    file = create_random_design()
    filename = f"design_{random.randint(1000,9999)}.png"
    upload_to_drive(file, filename)
