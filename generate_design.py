import os
import requests
from PIL import Image
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Fetch a design (adjust as needed for your API)
def fetch_craiyon(prompt):
    url = "https://api.craiyon.com/v3"
    response = requests.post(url, json={"prompt": prompt})
    response.raise_for_status()  # Will raise an exception for bad responses
    return response.json()

# Upload image to Google Drive
def upload_to_drive(image_path, folder_id):
    # Authenticate with Google Drive
    creds = service_account.Credentials.from_service_account_info(
        os.getenv("GOOGLE_CREDENTIALS")
    )
    service = build('drive', 'v3', credentials=creds)

    # Upload the file
    media = MediaFileUpload(image_path, mimetype='image/png')
    request = service.files().create(
        media_body=media,
        body={
            'name': os.path.basename(image_path),
            'parents': [folder_id]
        }
    )
    file = request.execute()
    return file['id']

# Main function to generate and upload the design
def main():
    prompt = "Minimalist geometric t-shirt design, bold lines and colors"
    print(f"Generating T-shirt design for prompt: {prompt}")

    try:
        # Get the design from Craiyon (or another model)
        images = fetch_craiyon(prompt)
        image_data = images['images'][0]  # Assuming the first image is what we want

        # Convert image data to PIL Image
        img = Image.open(BytesIO(image_data))
        img.save('design.png')

        # Upload to Google Drive
        folder_id = os.getenv("DRIVE_FOLDER_ID")
        upload_to_drive('design.png', folder_id)
        print("Design uploaded to Google Drive successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
