import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
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
    
    # Placeholder for actual design generation logic (e.g., use PIL, OpenCV, or any other method)
    time.sleep(2)  # Simulate time taken to create a design
    return filename

# Main logic to generate and upload the design
def main():
    folder_id = os.environ.get('DRIVE_FOLDER_ID')  # Ensure this environment variable is set in GitHub Actions

    if folder_id is None:
        raise ValueError("DRIVE_FOLDER_ID environment variable is not set.")

    # Generate a random design (simulated here, replace with actual design logic)
    design_filename = generate_design()

    # Simulate saving the design (replace with actual saving logic)
    # For example, save the design as PNG to a file
    design_file_path = f"./{design_filename}"

    # Simulate file creation by creating an empty file
    with open(design_file_path, 'w') as f:
        f.write("Design content placeholder")

    # Upload the design to Google Drive
    upload_to_drive(design_file_path, folder_id)

    # Optionally, remove the design file after upload
    os.remove(design_file_path)

if __name__ == '__main__':
    main()
