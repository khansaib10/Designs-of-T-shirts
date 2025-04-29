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

# ─── Config ────────────────────────────────────────────────────────────────────
# HuggingFace
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Google Drive (Service Account JSON stored in the secret GOOGLE_CREDENTIALS)
credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

FOLDER_ID = "1jnHnezrLNTl3ebmlt2QRBDSQplP_Q4wh"  # your Drive folder

# Fonts (must be uploaded in your repo)
FONTS = [
    "CalSans-Regular.ttf",
    "RobotoMono-VariableFont_wght.ttf",
    "Tagesschrift-Regular.ttf",
]

# Sample text list
TEXTS = [
    "Dream Big", "Stay Wild", "Good Vibes", "Be Different",
    "No Limits", "Fearless", "Born to Shine", "Stay Focused",
    "Create Your Future", "Unstoppable Energy"
]

# ─── Generate AI Background ───────────────────────────────────────────────────
def generate_ai_background():
    url = "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {
        "inputs": "beautiful colorful abstract background, vibrant, t-shirt design, no text, no watermark, hd, 3000x3000",
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        raise Exception(f"AI generation failed: {resp.text}")
    return Image.open(BytesIO(resp.content))

# ─── Compose Final Design ────────────────────────────────────────────────────
def create_design(bg: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(bg)

    # Pick text and font
    text = random.choice(TEXTS)
    font_path = random.choice(FONTS)
    font_size = random.randint(180, 250)
    font = ImageFont.truetype(font_path, font_size)

    # Measure and center
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (bg.width - text_w) / 2
    y = (bg.height - text_h) / 2

    # Draw drop-shadow
    for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
        draw.text((x+dx, y+dy), text, font=font, fill="black")
    # Draw main text
    draw.text((x, y), text, font=font, fill="white")

    return bg

# ─── Upload to Google Drive ───────────────────────────────────────────────────
def upload_to_drive(filepath: str):
    metadata = {"name": os.path.basename(filepath), "parents": [FOLDER_ID]}
    media = MediaFileUpload(filepath, mimetype="image/png")
    file = drive_service.files().create(
        body=metadata, media_body=media, fields="id"
    ).execute()
    print(f"Uploaded to Drive, file ID: {file['id']}")

# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    bg = generate_ai_background()
    final = create_design(bg)

    out_name = f"design_{random.randint(1000,9999)}.png"
    out_path = f"/tmp/{out_name}"
    final.save(out_path, format="PNG", dpi=(300,300))

    upload_to_drive(out_path)

if __name__ == "__main__":
    main()
