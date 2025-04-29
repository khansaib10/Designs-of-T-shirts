import os
import random
import string
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Load HuggingFace Token
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')

# Setup Google Drive
gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("credentials.json")
drive = GoogleDrive(gauth)

# Your Google Drive Folder ID
FOLDER_ID = "1jnHnezrLNTl3ebmlt2QRBDSQplP_Q4wh"

# Fonts you have
fonts = [
    "CalSans-Regular.ttf",
    "RobotoMono-VariableFont_wght.ttf",
    "Tagesschrift-Regular.ttf",
]

def generate_ai_background():
    print("Generating AI Background...")
    url = "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {
        "inputs": "beautiful colorful abstract background, vibrant, t-shirt design, no text, no watermark, hd, 3000x3000",
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to generate image: {response.text}")

    image = Image.open(BytesIO(response.content))
    return image

def create_design(background):
    print("Adding text and shapes...")
    draw = ImageDraw.Draw(background)

    # Random text
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    font_path = random.choice(fonts)
    font = ImageFont.truetype(font_path, random.randint(100, 200))

    # Text position
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    x = (background.width - text_width) // 2
    y = (background.height - text_height) // 2

    # Draw text
    draw.text((x, y), text, font=font, fill="white")

    # Draw random circles (shapes)
    for _ in range(5):
        radius = random.randint(50, 150)
        cx = random.randint(0, background.width)
        cy = random.randint(0, background.height)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color, outline=None)

    return background

def upload_to_drive(file_path):
    print(f"Uploading {file_path} to Google Drive...")
    file_drive = drive.CreateFile({'parents': [{'id': FOLDER_ID}]})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()
    print("Upload completed!")

def main():
    background = generate_ai_background()
    final_design = create_design(background)

    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12)) + ".png"
    file_path = f"/tmp/{filename}"
    final_design.save(file_path, format="PNG")

    upload_to_drive(file_path)

if __name__ == "__main__":
    main()
