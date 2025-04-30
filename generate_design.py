import os
import json
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Get environment variables
HORDE_API_KEY = os.getenv("HORDE_API_KEY")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
UPLOAD_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

if not HORDE_API_KEY:
    raise Exception("HORDE_API_KEY is missing in environment variables.")
if not GOOGLE_CREDENTIALS:
    raise Exception("GOOGLE_CREDENTIALS is missing in environment variables.")
if not UPLOAD_FOLDER_ID:
    raise Exception("UPLOAD_FOLDER_ID is missing in environment variables.")

def generate_ai_background(prompt="Minimalist t-shirt design, vector art, clean, simple, professional"):
    print("▶️ Submitting background generation to Stable Horde...")

    headers = {
        "apikey": HORDE_API_KEY,
        "Client-Agent": "TshirtDesignBot/1.0"
    }

    payload = {
        "prompt": prompt,
        "params": {
            "n": 1,
            "width": 512,
            "height": 512,
            "steps": 20,
            "seed": str(int(time.time()))
        },
        "model": "deliberate_v2",
        "nsfw": False,
        "censor_nsfw": True
    }

    try:
        submit_response = requests.post("https://stablehorde.net/api/v2/generate/async", headers=headers, json=payload)
        submit_response.raise_for_status()
        task_id = submit_response.json()["id"]
    except Exception as e:
        raise Exception(f"❌ Error submitting generation: {e}")

    print("⏳ Waiting for generation...")

    tries = 0
    while tries < 50:
        time.sleep(10)
        status_response = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", headers=headers)
        if status_response.status_code == 429:
            print("❌ Rate limit hit (429). Retrying after delay...")
            time.sleep(20)
            tries += 1
            continue

        status = status_response.json()
        if status.get("done"):
            if "generations" in status and len(status["generations"]) > 0:
                image_url = status["generations"][0]["img"]
                image_data = requests.get(image_url).content
                print("✅ Background generated successfully!")
                return Image.open(BytesIO(image_data))
            else:
                raise Exception("❌ No generations found.")
        tries += 1

    raise Exception("❌ Failed to generate background image after several attempts.")

def add_text_to_image(image, text="Stay Wild"):
    print("🖌 Adding text on design...")
    draw = ImageDraw.Draw(image)
    font_size = int(image.width / 10)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(text, font=font)
    x = (image.width - text_width) / 2
    y = image.height - text_height - 20

    draw.text((x, y), text, font=font, fill="black")
    return image

def upload_to_drive(file_path, file_name):
    print("☁️ Uploading design to Google Drive...")

    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    credentials = service_account.Credentials.from_service_account_info(json.loads(GOOGLE_CREDENTIALS))
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        "name": file_name,
        "parents": [UPLOAD_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype="image/png")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    print(f"✅ Uploaded successfully: {file.get('id')}")

def main():
    try:
        bg_image = generate_ai_background()
        final_image = add_text_to_image(bg_image)

        output_filename = "final_design.png"
        final_image.save(output_filename)

        upload_to_drive(output_filename, output_filename)

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
