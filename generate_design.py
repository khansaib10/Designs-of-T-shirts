import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageFont
import random
import string
import time

# Function to authenticate with Google API using the service account
def authenticate_google_drive():
    credentials = service_account.Credentials.from_service_account_file(
        'service_account.json',  # This will be created during the GitHub Actions step
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    return build('drive', 'v3', credentials=credentials)

# Function to create a random design name
def generate_random_filename():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.png'

# Function to create an image (for demonstration purposes, just a simple image with text)
def create_image(image_path):
    # Create a new blank image (RGB mode, 100x100 pixels, white background)
    img = Image.new('RGB', (100, 100), color='white')
    d = ImageDraw.Draw(img)

    # You can customize the font and text
    try:
        font = ImageFont.load_default()  # Load the default font
    except IOError:
        font = ImageFont.load_default()

    text = "Design"
    d.text((10, 40), text, fill=(0, 0, 0), font=font)

    # Save the image to the specified path
    img.save(image_path)

# Function to upload the design to Google Drive
def upload_to_drive(file_path, folder_id):
    drive_service = authenticate_google_drive()

    # Create the file metadata with the folder ID
    file_metadata = {
        'name': generate_random_filename(),
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype='image/png')

    # Upload the file
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"File uploaded: {file['id']}")

# Function to simulate design generation (replace with actual logic)
def generate_design():
    # Simulating the design creation process
    filename = generate_random_filename()
    print(f"Generating design: {filename}")
    
    # Create a valid image (replace with actual design generation logic)
    image_path = f"./{filename}"
    create_image(image_path)
    
    return image_path

# Main logic to generate and upload the design
def main():
    folder_id = os.environ.get('DRIVE_FOLDER_ID')  # Ensure this environment variable is set in GitHub Actions

    if folder_id is None:
        raise ValueError("DRIVE_FOLDER_ID environment variable is not set.")

    # Generate a random design (simulated here, replace with actual design logic)
    design_filename = generate_design()

    # Upload the design to Google Drive
    upload_to_drive(design_filename, folder_id)

    # Optionally, remove the design file after upload
    os.remove(design_filename)

if __name__ == '__main__':
    main()
