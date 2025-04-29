import os
import json
import time
import base64
import random
import string
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── CONFIG ───────────────────────────────────────────────────────────────────
# Stable Horde endpoints (anonymous mode)
HORDE_API_BASE = "https://stablehorde.net/api"
HORDE_API_KEY = "0000000000"  # anonymous; no signup, lowest priority

# Google Drive service-account JSON stored in the secret GOOGLE_CREDENTIALS
google_credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")  # set this secret too

# Scope and build Drive client
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
credentials = service_account.Credentials.from_service_account_info(
    google_credentials, scopes=SCOPES
)
drive_client = build("drive", "v3", credentials=credentials)
# ────────────────────────────────────────────────────────────────────────────────

def generate_ai_background(prompt: str="Colorful abstract t-shirt design") -> Image.Image:
    """Submit an async job to Stable Horde, poll until done, return PIL.Image."""
    print("▶️ Submitting background generation to Stable Horde...")
    payload = {
        "prompt": prompt,
        "params": {"n": 1, "width": 1024, "height": 1024},
        "api_key": HORDE_API_KEY
    }
    # 1) kick off job
    r = requests.post(f"{HORDE_API_BASE}/v2/generate/async", json=payload)
    r.raise_for_status()
    job_id = r.json()["id"]
    # 2) poll every 5s until done
    print(f"⏳ Waiting for job {job_id} to complete...")
    while True:
        time.sleep(5)
        status = requests.get(f"{HORDE_API_BASE}/v2/generate/check/{job_id}").json()
        if status.get("done"):
            break
    gen = status["generations"][0]["img"]
    # 3) decode base64
    img_data = base64.b64decode(gen)
    return Image.open(BytesIO(img_data))

def overlay_text(img: Image.Image, text: str) -> Image.Image:
    """Draw white text with black shadow at bottom center."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    font_size = W // 12
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    tw, th = draw.textsize(text, font=font)
    x, y = (W - tw)//2, H - th - 40
    # shadow
    for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
        draw.text((x+dx, y+dy), text, font=font, fill="black")
    draw.text((x, y), text, font=font, fill="white")
    return img

def save_and_upload(img: Image.Image):
    """Save locally, then upload to Drive folder."""
    fn = f"design_{''.join(random.choices(string.ascii_lowercase+string.digits, k=6))}.png"
    img.save(fn, format="PNG")
    print(f"💾 Saved as {fn}")
    # Upload
    file_meta = {"name": fn, "parents":[DRIVE_FOLDER_ID]}
    media = MediaFileUpload(fn, mimetype="image/png")
    uploaded = drive_client.files().create(body=file_meta, media_body=media, fields="id").execute()
    print(f"✅ Uploaded to Drive, file ID: {uploaded['id']}")

def main():
    try:
        bg = generate_ai_background()
        txt = random.choice([
            "Dream Big","Stay Wild","Good Vibes","Be Yourself","Adventure Awaits",
            "Born to Shine","Explore More","Live Free","Stay Strong"
        ])
        final = overlay_text(bg, txt)
        save_and_upload(final)
    except Exception as e:
        print("❌ Error:", e)

if __name__=="__main__":
    main()
