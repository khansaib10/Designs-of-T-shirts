import os
import json
import requests
from PIL import Image
from io import BytesIO
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Replace with your HuggingFace API Token
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
google_credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

# Set up Google Drive API
credentials = service_account.Credentials.from_service_account_info(
    google_credentials, scopes=["https://www.googleapis.com/auth/drive.file"]
)
drive_service = build("drive", "v3", credentials=credentials)

# Huggingface API URL and model
model_id = "runwayml/stable-diffusion-v1-5"  # Updated model
api_url = f"https://api-inference.huggingface.co/models/{model_id}"

# Generate AI Background
def generate_ai_background():
    print("Generating AI Background...")
    headers = {"Authorization": f"Bearer {huggingface_token}"}
    prompt = "t-shirt design background, vibrant, colorful, artistic"
    response = requests.post(api_url, headers=headers, json={"inputs": prompt})

    if response.status_code != 200:
        raise Exception(f"AI generation failed: {response.text}")

    image = Image.open(BytesIO(response.content))
    return image

# Upload image to Google Drive
def upload_to_drive(file_path, folder_id="root"):
    file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype="image/png")
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"Uploaded file with ID: {file['id']}")

# Main function to run the design generation and upload
def main():
    try:
        # Generate background
        bg_image = generate_ai_background()
        bg_image_path = "background_image.png"
        bg_image.save(bg_image_path)

        # Upload the background image to Google Drive
        upload_to_drive(bg_image_path)

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the script
if __name__ == "__main__":
    main()
