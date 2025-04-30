from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
import io
from googleapiclient.http import MediaIoBaseUpload

# Function to get a random quote
def get_quote():
    response = requests.get("https://api.quotable.io/random")
    if response.status_code == 200:
        quote = response.json()['content']
        return quote
    else:
        return "Default Quote"

# Function to generate the design
def create_design(text):
    # Set image size and quality
    width, height = 1024, 1024  # 1024x1024 for high quality
    font_size = 50  # Adjust the font size for better readability

    # Create an image with transparent background (RGBA)
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(image)

    # Use a good quality font (ensure this path exists or use a standard one)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Wrap the text
    margin = 100
    max_width = width - 2 * margin
    wrapped_text = textwrap.fill(text, width=25)  # Wrap text to fit the image

    # Draw the text onto the image
    y_offset = 100  # Adjust starting position
    for line in wrapped_text.split('\n'):
        width_text, height_text = draw.textsize(line, font)
        x = (width - width_text) // 2  # Center the text
        draw.text((x, y_offset), line, font=font, fill=(255, 255, 255, 255))  # White text
        y_offset += height_text + 10  # Adjust vertical spacing

    return image

# Function to upload the image to Google Drive
def upload_to_drive(image, filename):
    # Set up credentials and Google Drive service
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = 'path_to_your_service_account_file.json'
    
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)

    # Save image as PNG (high quality)
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
    
    # Generate design
    image = create_design(quote)
    
    # Filename based on the current timestamp
    filename = f"quote_{int(time.time())}.png"
    
    # Upload the image to Google Drive
    upload_to_drive(image, filename)

if __name__ == "__main__":
    main()
