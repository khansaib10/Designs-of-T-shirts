import os
import time
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load environment variables
HORDE_API_KEY = os.getenv("HORDE_API_KEY")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

if not HORDE_API_KEY:
    raise Exception("HORDE_API_KEY is missing in environment variables.")
if not GOOGLE_CREDENTIALS:
    raise Exception("GOOGLE_CREDENTIALS is missing in environment variables.")
if not DRIVE_FOLDER_ID:
    raise Exception("DRIVE_FOLDER_ID is missing in environment variables.")

# Function to generate AI background using Stable Horde
def generate_ai_background():
    print("▶️ Submitting background generation to Stable Horde...")

    url = "https://stablehorde.net/api/v2/generate/async"

    payload = {
        "prompt": "Minimalistic t-shirt design, plain background, professional vector art, simple, clean, modern",
        "params": {
            "n": 1,
            "width": 512,
            "height": 512,
            "sampler_name": "k_euler",
            "cfg_scale": 7,
            "steps": 20,
            "seed": str(int(time.time()))
        }
    }
    headers = {
        "apikey": HORDE_API_KEY,
        "Client-Agent": "TshirtDesignBot:1.0 (by user on horde)"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 202:
        raise Exception(f"❌ Error: {response.status_code} - ***{response.text}***")

    data = response.json()
    request_id = data.get('id')
    if not request_id:
        raise Exception("❌ No request ID received.")

    # Poll for completion
    status_url = f"https://stablehorde.net/api/v2/generate/check/{request_id}"
    attempts = 0
    print("⏳ Waiting for generation...")

    while attempts < 60:  # wait up to 10 minutes (60 x 10 seconds)
        time.sleep(10)
        status = requests.get(status_url, headers=headers)
        if status.status_code == 429:
            print("❌ Rate limit hit (429). Retrying after delay...")
            time.sleep(15)
            continue
        if status.status_code != 200:
            print(f"❌ Error checking status: {status.status_code}")
            continue
        status_data = status.json()
        if status_data.get("done"):
            generations = status_data.get("generations", [])
            if generations:
                img_url = generations[0]["img"]
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    return img_response.content
                else:
                    raise Exception(f"❌ Failed to download image: {img_response.status_code}")
            else:
                raise Exception("❌ No generations found.")
        attempts += 1

    raise Exception("❌ Failed to generate background image after several attempts.")

# Function to create final design
def create_final_design(bg_image_bytes):
    print("🎨 Creating final design...")

    # Load background
    bg = Image.open(io.BytesIO(bg_image_bytes)).convert("RGBA")

    # Add text
    draw = ImageDraw.Draw(bg)
    text = "Dream Big"
    font_size = 40
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Built-in font path
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (bg.width - text_width) / 2
    text_y = (bg.height - text_height) / 2

    draw.text((text_x, text_y), text, font=font, fill="black")

    output_path = "final_design.png"
    bg.save(output_path)

    return output_path

# Function to upload to Google Drive
def upload_to_drive(file_path):
    print("☁️ Uploading design to Google Drive...")

    credentials_dict = json.loads(GOOGLE_CREDENTIALS)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)

    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ Uploaded to Drive with file ID: {file.get('id')}")

# Main flow
def main():
    try:
        bg_image = generate_ai_background()
        design_path = create_final_design(bg_image)
        upload_to_drive(design_path)
        print("🎉 All Done Successfully!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    import io
    main()
