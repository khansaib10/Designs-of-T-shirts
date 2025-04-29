import os
import random
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Settings
FOLDER_ID = '1jnHnezrLNTl3ebmlt2QRBDSQplP_Q4wh'  # your Google Drive folder id
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Fonts (Make sure these font files are in your repo)
FONTS = [
    "CalSans-Regular.ttf",
    "RobotoMono-VariableFont_wght.ttf",
    "Tagesschrift-Regular.ttf"
]

# List of random quotes or words
TEXTS = [
    "Dream Big", "Stay Wild", "Good Vibes", "Be Different", "No Limits", "Fearless", "Born to Shine"
]

def generate_ai_background():
    url = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {"inputs": "abstract colorful background, 3000x3000, hd, no watermark, no text, t-shirt design"}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to generate image: {response.text}")
    
    image = Image.open(BytesIO(response.content))
    return image

def add_text_on_image(image):
    draw = ImageDraw.Draw(image)
    font_path = random.choice(FONTS)
    font = ImageFont.truetype(font_path, size=250)
    text = random.choice(TEXTS)
    
    # Get text size
    text_width, text_height = draw.textsize(text, font=font)
    image_width, image_height = image.size
    
    # Position text at center
    position = ((image_width - text_width) / 2, (image_height - text_height) / 2)
    
    draw.text(position, text, font=font, fill="white")  # White color text
    return image

def upload_to_drive(filepath):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    
    file_drive = drive.CreateFile({'parents': [{'id': FOLDER_ID}]})
    file_drive.SetContentFile(filepath)
    file_drive.Upload()
    print(f"Uploaded {filepath} to Google Drive.")

def main():
    print("Generating AI Background...")
    background = generate_ai_background()
    
    print("Adding Text...")
    final_image = add_text_on_image(background)
    
    filename = f"design_{random.randint(1000,9999)}.png"
    filepath = os.path.join(os.getcwd(), filename)
    final_image.save(filepath, format="PNG", quality=100)
    
    print("Uploading to Drive...")
    upload_to_drive(filepath)

if __name__ == "__main__":
    main()
