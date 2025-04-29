import random
import string
from PIL import Image, ImageDraw, ImageFont
import os
import json
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account

# ─── Google Drive Setup ─────────────────────────────────────────────────────
credentials_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
credentials = service_account.Credentials.from_service_account_info(credentials_info)
service = build('drive', 'v3', credentials=credentials)
folder_id = '1jnHnezrLNTl3ebmlt2QRBDSQplP_Q4wh'  # Your Drive folder ID

# ─── Design Generation ──────────────────────────────────────────────────────
def create_random_design():
    size = (3000, 3000)
    img = Image.new('RGBA', size, (0, 0, 0, 0))  # Transparent canvas
    draw = ImageDraw.Draw(img)

    # 1. Draw random shapes first
    for _ in range(random.randint(5, 10)):
        shape_type = random.choice(['circle', 'rectangle', 'line'])
        color = random.choice(['#FF5733', '#33FF57', '#3357FF', '#F333FF', '#33FFF6', '#FFF633'])
        x1 = random.randint(0, size[0])
        y1 = random.randint(0, size[1])
        x2 = random.randint(0, size[0])
        y2 = random.randint(0, size[1])

        if shape_type == 'circle':
            bbox = [min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)]
            draw.ellipse(bbox, outline=color, width=10)
        elif shape_type == 'rectangle':
            bbox = [min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)]
            draw.rectangle(bbox, outline=color, width=10)
        elif shape_type == 'line':
            draw.line([x1, y1, x2, y2], fill=color, width=8)

    # 2. Random motivational word
    words = ['Dream', 'Freedom', 'Hustle', 'Create', 'Inspire', 'Legend', 'Fearless', 'Ambition', 'Grind', 'Passion']
    txt = random.choice(words)

    # 3. Pick a random font
    fonts = [
        "CalSans-Regular.ttf"
        "SomeOtherFont.ttf",  # Upload more fonts and list them here
        "Tagesschrift-Regular.ttf",
    ]
    selected_font = random.choice(fonts)
    fontsize = random.randint(350, 600)
    try:
        fnt = ImageFont.truetype(selected_font, fontsize)
    except:
        print(f"Failed loading font {selected_font}, using default font.")
        fnt = ImageFont.load_default()

    # 4. Measure text size and center it
    bbox = draw.textbbox((0, 0), txt, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size[0] - tw) / 2
    y = (size[1] - th) / 2

    # 5. Draw the big text in a strong color
    text_color = random.choice(['#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF'])
    draw.text((x, y), txt, font=fnt, fill=text_color)

    # 6. Save to BytesIO with 300 DPI
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG', dpi=(300, 300))
    img_byte_arr.seek(0)

    return img_byte_arr

# ─── Upload to Google Drive ──────────────────────────────────────────────────
def upload_to_drive(file_bytes, filename):
    metadata = {
        'name': filename,
        'parents': [folder_id],
        'mimeType': 'image/png'
    }
    media = MediaIoBaseUpload(file_bytes, mimetype='image/png')
    file = service.files().create(body=metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {filename} as ID: {file.get('id')}")

# ─── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    img_stream = create_random_design()
    fname = f"design_{random.randint(1000,9999)}.png"
    upload_to_drive(img_stream, fname)
