from PIL import Image
from PIL.ExifTags import TAGS
import sys

def xray_image(image_path):
    print(f"--- Scanning {image_path} ---")
    try:
        img = Image.open(image_path)
        exif = img._getexif()

        if not exif:
            print("❌ RESULT: NO EXIF DATA AT ALL! The transfer method stripped it.")
            return

        print("✅ EXIF Data Found! Here is what is inside:")
        found_gps = False
        
        for tag_id, value in exif.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == 'GPSInfo':
                found_gps = True
                print(f"📍 GPSInfo: {value}")
            elif tag_name == 'DateTimeOriginal':
                print(f"🕒 DateTimeOriginal: {value}")
            elif tag_name in ['Make', 'Model']:
                print(f"📱 Camera: {value}")

        if not found_gps:
            print("\n❌ RESULT: EXIF exists, but GPS was stripped out by your phone's privacy settings.")

    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == '__main__':
    # Change this filename to the EXACT name of the image sitting in your VS Code uploads folder!
    # Example: "uploads/site_myphoto.jpg"
    test_image = "uploads/S1.jpg" 
    xray_image(test_image)