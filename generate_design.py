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

# ─── Quotes List ────────────────────────────────────────────────────────────
quotes = [
    "Dream Big", "Stay Strong", "Work Hard", "Never Quit",
    "Chase Dreams", "Be Fearless", "Rise Above", "Stay Humble",
    "Create Yourself", "Bold Moves", "Fear Less", "Mind Over Matter",
    "Be Your Best", "Good Vibes", "Limitless", "Focused Energy",
    "Make It Happen", "Stay Positive", "Push Yourself", "Stay Focused"
]

# ─── Fonts List ─────────────────────────────────────────────────────────────
fonts = [
    "CalSans-Regular.ttf",
    "RobotoMono-VariableFont_wght.ttf",
    "Tagesschrift-Regular.ttf"
]

# ─── Design Generation ──────────────────────────────────────────────────────
def create_premium_design():
    size = (3000, 3000)
    img = Image.new('RGBA', size, (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    # 1. Select random quote and font
    quote = random.choice(quotes)
    words = quote.split()
    
    # 2. Random font and size
    font_file = random.choice(fonts)
    fontsize = random.randint(350, 550)
    fnt = ImageFont.truetype(font_file, fontsize)

    # 3. Split text if 3 words
    if len(words) > 2:
        quote = f"{words[0]} {words[1]}\n{words[2]}"
    
    # 4. Calculate text size
    bbox = draw.textbbox((0, 0), quote, font=fnt, align='center')
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 5. Center position
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2

    # 6. Draw text
    text_color = random.choice(["#000000", "#ffffff"])  # Black or White
    draw.text((x, y), quote, font=fnt, fill=text_color, align="center")

    # 7. Draw underline
    underline_width = text_width * 0.6
    underline_height = 10  # thickness
    underline_x1 = (size[0] - underline_width) / 2
    underline_y1 = y + text_height + 30
    underline_x2 = underline_x1 + underline_width
    underline_y2 = underline_y1 + underline_height
    draw.rectangle([underline_x1, underline_y1, underline_x2, underline_y2], fill=text_color)

    # 8. Optional minimal decoration (stars/dots)
    if random.random() < 0.5:  # 50% chance
        # Draw small star/dot at top center
        deco_size = 20
        deco_x = size[0] / 2 - deco_size / 2
        deco_y = y - 100
        draw.ellipse([deco_x, deco_y, deco_x + deco_size, deco_y + deco_size], fill=text_color)

    # 9. Save as PNG 300DPI
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
    img_stream = create_premium_design()
    fname = f"design_{random.randint(1000,9999)}.png"
    upload_to_drive(img_stream, fname)
