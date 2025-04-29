import os
import json
import random
import string
import time
import requests
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
HORDE_API_KEY = os.getenv("HORDE_API_KEY")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

if not HORDE_API_KEY:
    raise Exception("❌ HORDE_API_KEY environment variable is missing!")

# Function to generate a random T-shirt slogan
def generate_random_text():
    words = ["Adventure", "Dream", "Freedom", "Passion", "Inspire", "Believe", "Create", "Explore", "Imagine", "Shine"]
    return random.choice(words)

# Function to generate a unique file name
def generate_unique_filename():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + ".png"

# Function to generate an AI background using Stable Horde
def generate_ai_background():
    print("▶️ Submitting background generation to Stable Horde...")
    url = "https://stablehorde.net/api/v2/generate/async"

    payload = {
        "prompt": "minimalist modern abstract background, colorful, artistic design, t-shirt print, white background",
        "params": {
            "sampler_name": "k_euler",
            "cfg_scale": 7,
            "denoising_strength": 0.75,
            "seed": str(random.randint(1, 1000000)),  # FIX: make seed a string
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

    # Poll for status with rate limiting handling (retry after delay)
    print("⏳ Waiting for generation...")

    retries = 5  # Retry 5 times before giving up
    while retries > 0:
        status_url = f"https://stablehorde.net/api/v2/generate/status/{request_id}"
        status_resp = requests.get(status_url, headers=headers)

        if status_resp.status_code == 429:
            print("❌ Rate limit hit (429). Retrying after delay...")
            time.sleep(10)  # Wait 10 seconds before retrying
            retries -= 1
            continue

        if status_resp.status_code != 200:
            print(f"❌ Error checking status: {status_resp.status_code}")
            break

        status_data = status_resp.json()

        # Check if 'done' key exists in the response data
        if 'done' not in status_data:
            print("❌ Error: 'done' key not found in response")
            break

        if status_data['done']:
            generations = status_data.get('generations', [])
            if not generations:
                print("❌ Error: No generations found.")
                break

            img_url = generations[0]['img']
            img_resp = requests.get(f"https://stablehorde.net{img_url}")

            with open("background.png", "wb") as f:
                f.write(img_resp.content)

            print("✅ AI Background generated and saved as background.png")
            return "background.png"

        time.sleep(5)  # Wait 5 seconds before checking status again

    raise Exception("❌ Failed to generate background image after several attempts.")

# Function to create a T-shirt design
def create_design(bg_image_path, text):
    print("🎨 Creating final design...")
    img = Image.open(bg_image_path)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(text, font=font)
    x = (img.width - text_width) / 2
    y = img.height - text_height - 20

    draw.text((x, y), text, font=font, fill=(0, 0, 0))

    filename = generate_unique_filename()
    img.save(filename)
    print(f"✅ Final design saved as {filename}")
    return filename

# Main function
def main():
    try:
        bg_image = generate_ai_background()
        if not bg_image:
            raise Exception("❌ Background generation failed, no image returned.")
        slogan = generate_random_text()
        final_design = create_design(bg_image, slogan)

        # Done! You can later upload it to Google Drive here if you want
        print(f"🎉 Finished! Design ready: {final_design}")

    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
