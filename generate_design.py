import os
import json
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set up Google Drive API
credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build('drive', 'v3', credentials=credentials)

# Folder ID where images will be uploaded
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# Horde API
HORDE_API_KEY = os.getenv("HORDE_API_KEY")

def generate_ai_background():
    print("▶️ Submitting background generation to Stable Horde...")
    url = "https://stablehorde.net/api/v2/generate/async"

    payload = {
        "prompt": "minimalist modern abstract background, colorful, artistic design, t-shirt print, white background",
        "params": {
            "sampler_name": "k_euler",
            "cfg_scale": 7,
            "denoising_strength": 0.75,
            "seed": random.randint(1, 1000000),
            "height": 512,
            "width": 512,
            "steps": 30
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["deliberate_v2"],
        "r2": True
    }

    headers = {
        "apikey": HORDE_API_KEY,
        "Client-Agent": "TShirtBot/1.0"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 202:
        raise Exception(f"❌ Error: {response.status_code} - {response.text}")

    data = response.json()
    request_id = data['id']

    # Poll for the result
    print("⏳ Waiting for generation...")
    status_url = f"https://stablehorde.net/api/v2/generate/status/{request_id}"

    while True:
        status_resp = requests.get(status_url, headers=headers)
        status_data = status_resp.json()

        if status_data['done']:
            generations = status_data.get('generations', [])
            if not generations:
                raise Exception("❌ No generations received.")

            img_url = generations[0]['img']
            img_resp = requests.get(f"https://stablehorde.net{img_url}")

            with open("background.png", "wb") as f:
                f.write(img_resp.content)

            print("✅ AI Background generated and saved as background.png")
            return "background.png"
        
        import time
        time.sleep(5)

def create_tshirt_design(background_path):
    img = Image.open(background_path).convert("RGBA")
    txt = Image.new('RGBA', img.size, (255,255,255,0))

    draw = ImageDraw.Draw(txt)

    # Random phrase
    phrases = ["Dream Big", "Stay Cool", "Ride Free", "Wild Soul", "Urban Vibes"]
    phrase = random.choice(phrases)

    # Load a basic font
    font = ImageFont.load_default()

    text_width, text_height = draw.textsize(phrase, font=font)
    position = ((img.width - text_width) // 2, (img.height - text_height) // 2)

    draw.text(position, phrase, font=font, fill=(0, 0, 0, 255))

    combined = Image.alpha_composite(img, txt)
    design_path = "tshirt_design.png"
    combined.save(design_path)

    print(f"✅ T-shirt design created: {design_path}")
    return design_path

def upload_to_drive(file_path):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [GOOGLE_DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype='image/png')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ Uploaded {file_path} to Google Drive with ID: {file.get('id')}")

def main():
    try:
        bg_image = generate_ai_background()
        tshirt_design = create_tshirt_design(bg_image)
        upload_to_drive(tshirt_design)
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
