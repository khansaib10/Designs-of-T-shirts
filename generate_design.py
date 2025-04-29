import os, json, random, string
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def create_random_design():
    w, h = 800, 800
    img = Image.new('RGB', (w, h), 'white')
    draw = ImageDraw.Draw(img)
    # draw rectangle
    x1, y1 = random.randint(0, w//2), random.randint(0, h//2)
    x2, y2 = random.randint(w//2, w), random.randint(h//2, h)
    draw.rectangle([x1, y1, x2, y2], fill=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    # draw circle
    r = random.randint(50,150)
    cx, cy = random.randint(r, w-r), random.randint(r, h-r)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
    # add text
    txt = ''.join(random.choices(string.ascii_uppercase+string.digits, k=8))
    fnt = ImageFont.load_default()
    tw, th = draw.textsize(txt, fnt)
    draw.text(((w-tw)/2,(h-th)/2), txt, font=fnt, fill='black')
    fname = f"design_{random.randint(1,9999)}.png"
    img.save(fname)
    return fname

def authenticate_drive():
    creds_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    creds = service_account.Credentials.from_service_account_info(
        creds_info, scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    return build('drive','v3',credentials=creds)

def upload_to_drive(fname):
    drive = authenticate_drive()
    folder_id = '1jnHnezrLNTl3ebmlt2QRBDSQplP_Q4wh'
    meta = {'name': fname, 'parents': [folder_id]}
    media = MediaFileUpload(fname, mimetype='image/png')
    drive.files().create(body=meta, media_body=media).execute()
    print(f"Uploaded {fname}")

if __name__ == "__main__":
    file = create_random_design()
    upload_to_drive(file)
