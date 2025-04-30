import os
import requests
from PIL import Image
from io import BytesIO

# Craiyon API endpoint
API_URL = "https://api.craiyon.com/v3"

# Function to fetch images from Craiyon API
def fetch_craiyon(prompt: str):
    response = requests.post(API_URL, json={"prompt": prompt})
    response.raise_for_status()
    data = response.json()

    images = []
    for img_url in data.get("images", []):
        # Download each image and open with Pillow
        img_response = requests.get(img_url)
        img_response.raise_for_status()
        images.append(Image.open(BytesIO(img_response.content)))
    return images

# Function to save images
def save_images(images, folder_id):
    for i, img in enumerate(images):
        # Save images to local file system or Google Drive as needed
        img_path = f"tshirt_design_{i}.png"
        img.save(img_path)
        print(f"Saved: {img_path}")
        
        # Here you can also upload to Google Drive (requires additional logic)

# Main function
def main():
    # Check for necessary environment variables
    if not os.getenv("DRIVE_FOLDER_ID"):
        raise Exception("DRIVE_FOLDER_ID is missing in environment variables.")
    
    prompt = "Minimalist geometric t-shirt design, bold lines and colors"
    print(f"Generating T-shirt design for prompt: {prompt}")
    
    # Fetch images from Craiyon API
    images = fetch_craiyon(prompt)
    
    # Save images locally or upload to Google Drive
    save_images(images, os.getenv("DRIVE_FOLDER_ID"))

if __name__ == "__main__":
    main()
