import random
import string
from PIL import Image, ImageDraw, ImageFont
import os
import json
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account

# ─── Google Drive Setup ──────────────────────────────────────────────────────────
credentials_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
credentials = service_account.Credentials.from_service_account_info(credentials_info)
service = build('drive', 'v3', credentials=credentials)
folder_id = '1jnHnezrLNTl3ebmlt2QRBDSQplP_Q4wh'  # Your Drive folder

# ─── Design Generation ──────────────────────────────────────────────────────────
def create_random_design():
    # 1) Bigger canvas for print-quality
    size = (3000, 3000)
    img = Image.new('RGBA', size, (0, 0, 0, 0))  # Transparent
    draw = ImageDraw.Draw(img)

    # 2) Pick a motivational word
    words = ['Dream', 'Freedom', 'Hustle', 'Create', 'Inspire', 'Legend', 'Fearless', 'Ambition', 'Grind', 'Passion']
    txt = random.choice(words)

    # 3) Choose font size (proportional to canvas)
    fontsize = random.randint(350, 600)

    # 4) Load your Tagesschrift font
    try:
        fnt = ImageFont.truetype("Tagesschrift-Regular.ttf", fontsize)
    except Exception as e:
        print("Font load failed, using default.", e)
        fnt = ImageFont.load_default()

    # 5) Measure text and center it
    bbox = draw.textbbox((0, 0), txt, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size[0] - tw) / 2
    y = (size[1] - th) / 2

    # 6) Draw the text in a bright color
    color = random.choice(['#000000', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'])
    draw.text((x, y), txt, font=fnt, fill=color)

    # 7) Save to a BytesIO with 300 DPI
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', dpi=(300, 300))
    img_bytes.seek(0)
    return img_bytes

# ─── Upload to Google Drive ────────────────────────────────────────────────────
def upload_to_drive(file_bytes, filename):
    metadata = {
        'name': filename,
        'parents': [folder_id],
        'mimeType': 'image/png'
    }
    media = MediaIoBaseUpload(file_bytes, mimetype='image/png')
    file = service.files().create(body=metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {filename} as ID: {file.get('id')}")

# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img_stream = create_random_design()
    fname = f"design_{random.randint(1000,9999)}.png"
    upload_to_drive(img_stream, fname)
