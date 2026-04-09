from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import os
from PIL import Image, ExifTags
import io

# --- NEW: Cloudinary Imports ---
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
# Import your cloud database connection
from backend.database import get_db_connection, get_cursor
load_dotenv()
app = FastAPI(title="AI Construction Enterprise Server")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)



class LoginRequest(BaseModel):
    user_id: int
    password: str

# 1. Secure Authentication Endpoint
@app.post("/api/login")
def login(request: LoginRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
        
    cursor = get_cursor(conn)
    cursor.execute("SELECT * FROM Users WHERE user_id = %s AND password = %s", (request.user_id, request.password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {"status": "success", "user": {"name": user["name"], "role": user["role"]}}
    raise HTTPException(status_code=401, detail="Invalid Enterprise Credentials")

# 2. Get Contractor Projects
@app.get("/api/projects/contractor/{contractor_id}")
def get_contractor_projects(contractor_id: int):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute("SELECT * FROM Projects WHERE contractor_id = %s", (contractor_id,))
    projects = cursor.fetchall()
    conn.close()
    return {"status": "success", "data": projects}


# 3. Get Public Projects (Upgraded with SQL JOIN)
@app.get("/api/projects/public")
def get_public_projects():
    conn = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute('''
        SELECT Projects.*, Users.name AS contractor_name 
        FROM Projects 
        LEFT JOIN Users ON Projects.contractor_id = Users.user_id
    ''')
    
    projects = cursor.fetchall()
    conn.close()
    return {"status": "success", "data": projects}

# 4. Public Timeline Endpoint 
@app.get("/api/public/updates/{project_id}")
def get_public_updates(project_id: int):
    conn = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute('''
        SELECT update_id as rowid, * FROM Updates 
        WHERE project_id = %s AND ai_verification_status = 'Verified'
        ORDER BY update_id DESC
    ''', (project_id,))
    updates = cursor.fetchall()
    conn.close()
    return {"status": "success", "data": updates}

# 5. THE NEW CLOUD UPLOAD ENDPOINT
@app.post("/api/updates")
async def upload_update(
    project_id: int = Form(...),
    stage_id: int = Form(...),
    uploaded_by: int = Form(...),
    claimed_progress: float = Form(...),
    cost_incurred_today: float = Form(...),
    site_image: UploadFile = File(...),
    bill_image: UploadFile = File(None)
):
    try:
        # 1. Beam the Site Image to Cloudinary
        site_result = cloudinary.uploader.upload(site_image.file)
        cloud_image_url = site_result.get("secure_url")

        # 2. Beam the Bill Image to Cloudinary (if provided)
        cloud_bill_url = None
        if bill_image:
            bill_result = cloudinary.uploader.upload(bill_image.file)
            cloud_bill_url = bill_result.get("secure_url")

        # 3. REAL AI VERIFICATION & ANTI-SPOOFING
        # We read the raw file data to check if it's a screenshot or real photo
        site_image.file.seek(0) # Reset file pointer
        raw_image_data = site_image.file.read()
        
        try:
            img = Image.open(io.BytesIO(raw_image_data))
            exif_data = img.getexif()
            is_real_camera = False
            if exif_data:
                for tag_id in exif_data:
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag_name in ['DateTimeOriginal', 'Make', 'Model', 'GPSInfo']:
                        is_real_camera = True
                        break
            
            if not is_real_camera:
                verification_status = "Flagged"
                print("🚨 AI Alert: Image lacks physical camera hardware tags!")
            else:
                verification_status = "Verified"
                
        except Exception as e:
            print(f"Image processing error: {e}")
            verification_status = "Flagged"
        # 4. Insert the Cloud URLs into the Supabase Database
        conn = get_db_connection()
        cursor = get_cursor(conn)
        cursor.execute('''
            INSERT INTO Updates 
            (project_id, stage_id, uploaded_by, image_file_path, bill_image_path, claimed_progress, cost_incurred_today, ai_verification_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (project_id, stage_id, uploaded_by, cloud_image_url, cloud_bill_url, claimed_progress, cost_incurred_today, verification_status))
        
        # 5. Update Project Master Totals
        cursor.execute('''
            UPDATE Projects 
            SET health_score = %s, actual_spent = actual_spent + %s 
            WHERE project_id = %s
        ''', (claimed_progress, cost_incurred_today, project_id))
        
        conn.commit()
        conn.close()

        return {"status": "success", "message": "AI Verification Complete. Assets secured in Cloud CDN."}

    except Exception as e:
        print(f"Cloud Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")    
