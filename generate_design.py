import os
import base64
import json
import random
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import time  # Corrected to use the time module

# Fetch a random quote from quotable.io API
def get_quote():
    try:
        response = requests.get("https://api.quotable.io/random", verify=False)  # Disabled SSL verification for now
        response.raise_for_status()  # Raise an exception for HTTP errors
        quote = response.json()["content"]
        return quote
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch quote: {e}")
        return "Stay positive and keep pushing."

# Create a t-shirt design based on the quote
def create_design(quote):
    # Set image size and background color (transparent)
    image = Image.new("RGBA", (1000, 1000), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(image)

    # Set font size and path (use a standard font or specify a font path)
    try:
        font = ImageFont.truetype("arial.ttf", 48)  # Adjust font and size as needed
    except IOError:
        font = ImageFont.load_default()  # Fallback if arial is unavailable

    # Wrap text to fit the design
    wrapped_text = textwrap.fill(quote, width=30)

    # Draw the text onto the image
    draw.text((50, 200), wrapped_text, font=font, fill="black")

    return image

# Upload the design to Google Drive
def upload_to_drive(image, filename):
    # Get base64-encoded credentials from environment
    encoded_credentials = os.environ['google_credential']

    # Decode from base64
    credentials_json = base64.b64decode(encoded_credentials).decode('utf-8')

    # Load JSON credentials
    credentials_info = json.loads(credentials_json)

    # Authenticate to Google Drive
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    service = build('drive', 'v3', credentials=credentials)

    # Save image to a BytesIO buffer
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # Upload to Google Drive
    file_metadata = {'name': filename}
    media = MediaIoBaseUpload(buffer, mimetype='image/png')
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# Main function to fetch the quote, create the design, and upload it
def main():
    # Fetch a random quote
    quote = get_quote()

    # Create design based on the quote
    image = create_design(quote)

    # Generate a unique filename using timestamp
    filename = f"quote_{int(time.time())}.png"  # Fixed to use time.time()

    # Upload the design to Google Drive
    upload_to_drive(image, filename)

if __name__ == "__main__":
    main()
