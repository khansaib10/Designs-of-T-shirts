import os
import io
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import time

# Get random quote from Quotable API
def get_quote():
    try:
        response = requests.get("https://api.quotable.io/random", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['content']
    except Exception as e:
        print(f"Failed to fetch quote: {e}")
        return "Stay positive and keep pushing."

# Create transparent high-quality design
def create_design(quote):
    # Create a transparent image (4000x4000px for T-shirt quality)
    width, height = 4000, 4000
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))  # Transparent

    draw = ImageDraw.Draw(image)

    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", size=180)
    except:
        font = ImageFont.load_default()

    # Split quote into multiple lines if too long
    lines = []
    words = quote.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width > width * 0.8:
            lines.append(line)
            line = word
        else:
            line = test_line
    lines.append(line)

    # Calculate total text height
    total_text_height = sum(draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] for l in lines)
    y = (height - total_text_height) // 2

    # Draw each line centered
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        x = (width - line_width) // 2
        draw.text((x, y), line, fill=(0, 0, 0, 255), font=font)  # Black text
        y += line_height + 20  # 20px between lines

    return image

# Upload image to Google Drive
def upload_to_drive(image, filename):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    # Read credentials from environment variable
    credentials_info = json.loads(os.environ['GDRIVE_CREDENTIALS'])
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=SCOPES
    )

    drive_service = build('drive', 'v3', credentials=credentials)

    # Save image to memory
    with io.BytesIO() as image_stream:
        image.save(image_stream, format='PNG')
        image_stream.seek(0)
        media = MediaIoBaseUpload(image_stream, mimetype='image/png', resumable=True)

        file_metadata = {'name': filename, 'mimeType': 'image/png'}
        drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# Main function
def main():
    quote = get_quote()
    print(f"Quote: {quote}")

    image = create_design(quote)
    filename = f"quote_{int(time.time())}.png"

    upload_to_drive(image, filename)

if __name__ == "__main__":
    main()
