import os
import time
import base64
import random
import string
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Craiyon v1 endpoint (no auth needed)
CRAIYON_URL = "https://backend.craiyon.com/generate"

def fetch_craiyon_images(prompt: str):
    """Call Craiyon v1 API, return list of PIL.Images."""
    print(f"🖌️  Sending prompt to Craiyon: {prompt!r}")
    resp = requests.post(CRAIYON_URL, json={"prompt": prompt}, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    images = []
    for b64 in data.get("images", []):
        img = Image.open(BytesIO(base64.b64decode(b64)))
        images.append(img)
    return images

def save_images(images):
    """Save a list of PIL.Images to numbered PNG files."""
    saved = []
    for i, img in enumerate(images):
        fn = f"design_{int(time.time())}_{i}.png"
        img.save(fn)
        print(f"✅ Saved {fn}")
        saved.append(fn)
    return saved

def overlay_text(img: Image.Image, text: str):
    """Overlay centered text with a black shadow."""
    draw = ImageDraw.Draw(img)
    W, H = img.size
    font_size = W // 12
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    tw, th = draw.textsize(text, font=font)
    x, y = (W - tw)//2, H - th - 20
    for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
        draw.text((x+dx, y+dy), text, font=font, fill="black")
    draw.text((x, y), text, font=font, fill="white")
    return img

def main():
    prompt = "Minimalist geometric t-shirt design, bold lines and colors"
    images = fetch_craiyon_images(prompt)

    # Optionally overlay text on each design:
    final_files = []
    for img in images:
        slogan = random.choice(["Dream Big","Stay Wild","Good Vibes","Be Yourself"])
        img = overlay_text(img.convert("RGBA"), slogan)
        # Convert back to RGB before saving
        img = img.convert("RGB")
        final_files.extend(save_images([img]))

    print("🎉 All done. Generated files:", final_files)

if __name__ == "__main__":
    main()
