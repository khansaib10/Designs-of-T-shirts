import os
import time
import json
import requests
import string
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ─── Configuration ────────────────────────────────────────────────────────────
DRIVE_FOLDER_ID    = os.getenv("DRIVE_FOLDER_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
if not DRIVE_FOLDER_ID or not GOOGLE_CREDENTIALS:
    raise Exception("Please set DRIVE_FOLDER_ID and GOOGLE_CREDENTIALS env vars.")
# ────────────────────────────────────────────────────────────────────────────────

def fetch_quote(max_length=50):
    """Fetch a single random quote up to max_length characters."""
    resp = requests.get(f"https://api.quotable.io/random?maxLength={max_length}", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return f"{data['content']} —{data['author']}"

def save_quote_to_file(quote):
    """Save quote to a timestamped .txt file."""
    ts = int(time.time())
    fn = f"quote_{ts}.txt"
    with open(fn, "w", encoding="utf-8") as f:
        f.write(quote)
    return fn

def upload_to_drive(filepath):
    """Upload a local file to Google Drive folder."""
    creds_info = json.loads(GOOGLE_CREDENTIALS)
    creds = service_account.Credentials.from_service_account_info(
        creds_info, scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": os.path.basename(filepath), "parents": [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(filepath, mimetype="text/plain")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file.get("id")

def main():
    try:
        quote = fetch_quote(max_length=50)
        print("Fetched quote:", quote)
        filename = save_quote_to_file(quote)
        print("Saved locally as", filename)
        file_id = upload_to_drive(filename)
        print("Uploaded to Drive with ID:", file_id)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
