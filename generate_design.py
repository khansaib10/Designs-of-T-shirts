from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
import time
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account

# Get quote from working API
def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            return data[0]["q"]  # Get quote text
        else:
            return "Stay positive and keep moving."
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return "Stay positive and keep moving."

# Function to generate the design
def create_design(text):
    width, height = 2048, 2048  # High resolution
    font_size = 100

    # Transparent background
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    margin = 100
    max_width = width - 2 * margin
    wrapped_text = textwrap.fill(text, width=20)

    y_offset = 400
    for line in wrapped_text.split('\n'):
        # Calculate text size correctly
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]

        x = (width - line_width) // 2
        draw.text((x, y_offset), line, font=font, fill=(255, 255, 255, 255))
        y_offset += line_height + 20

    return image

# Function to upload to Google Drive
def upload_to_drive(image, filename):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)

    with io.BytesIO() as image_stream:
        image.save(image_stream, format='PNG')
        image_stream.seek(0)
        media = MediaIoBaseUpload(image_stream, mimetype='image/png', resumable=True)

        file_metadata = {'name': filename, 'mimeType': 'image/png'}
        drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# Main
def main():
    quote = get_quote()
    print(f"Quote: {quote}")

    image = create_design(quote)
    filename = f"quote_{int(time.time())}.png"
    upload_to_drive(image, filename)

if __name__ == "__main__":
    main()
