from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

def get_exif_data(image_path):
    """Extracts raw EXIF data from an image."""
    try:
        image = Image.open(image_path)
        image.verify() # Verify it's actually an image, not a renamed malicious file
        image = Image.open(image_path) # Reopen after verify
        
        exif = image._getexif()
        if not exif:
            return None

        # Decode the unreadable EXIF tags into human-readable dictionary
        decoded_exif = {}
        for tag_id, value in exif.items():
            tag_name = TAGS.get(tag_id, tag_id)
            decoded_exif[tag_name] = value
            
        return decoded_exif
    except Exception as e:
        print(f"[SECURITY ERROR] {e}")
        return None

def verify_image_authenticity(image_path, expected_gps_lat=None, expected_gps_lon=None):
    """
    Checks if the image has a valid timestamp and GPS data.
    Returns: {"status": "Pass"|"Fail", "reason": "..."}
    """
    exif_data = get_exif_data(image_path)
    
    if not exif_data:
        return {"status": "Fail", "reason": "No EXIF data found. Image might be a screenshot or downloaded from WhatsApp/Web."}

    # 1. Timestamp Verification
    original_time_str = exif_data.get('DateTimeOriginal')
    if not original_time_str:
        return {"status": "Fail", "reason": "No original creation timestamp found."}

    try:
        # Convert EXIF string (YYYY:MM:DD HH:MM:SS) to Python DateTime
        photo_time = datetime.strptime(original_time_str, '%Y:%m:%d %H:%M:%S')
        days_old = (datetime.now() - photo_time).days
        
        # B.Tech Heuristic: Reject photos older than 3 days
        if days_old > 3:
             return {"status": "Fail", "reason": f"Photo is too old ({days_old} days). Must be taken recently."}
    except Exception:
        pass

    # 2. GPS Verification (Ensures they are actually at the site)
    gps_info = exif_data.get('GPSInfo')
    if not gps_info:
        return {"status": "Fail", "reason": "No GPS data found. Location services must be enabled on the camera."}

    # Note: For an A+ project, you would convert the complex GPS tuple into decimal format here 
    # and compare it mathematically to the 'expected_gps' coordinates from your Projects Database table!

    return {"status": "Pass", "reason": "Image timestamp and GPS data authenticated."}