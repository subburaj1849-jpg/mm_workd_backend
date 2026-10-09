from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, Admin, Staff, Attendance
import datetime
import os
import shutil

app = FastAPI(title="M.M Electrical and Plumbing Works API")

# Chrome browser connection allow panna CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload pannura photo save panna folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Flutter Login model
class LoginRequest(BaseModel):
    pin: str

@app.get("/")
def home():
    return {"message": "M.M Works Server Running Successfully!"}

# Flutter App Staff PIN Login API
@app.post("/api/login")
def api_login(req: LoginRequest, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.pin == req.pin).first()
    if not staff:
        raise HTTPException(status_code=401, detail="Invalid PIN! Try again.")
    return {
        "status": "success",
        "staff_id": staff.staff_id,
        "name": staff.name,
        "role": staff.role
    }

# Admin: Add Staff
class StaffCreateRequest(BaseModel):
    staff_id: str
    name: str
    phone: str
    role: str
    pin: str

@app.post("/admin/add-staff")
def add_staff(req: StaffCreateRequest, db: Session = Depends(get_db)):
    existing = db.query(Staff).filter(Staff.staff_id == req.staff_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Staff ID already exists!")
    new_staff = Staff(
        staff_id=req.staff_id,
        name=req.name,
        phone=req.phone,
        role=req.role,
        pin=req.pin
    )
    db.add(new_staff)
    db.commit()
    return {"status": "success", "message": f"Staff {req.name} created successfully!"}

# Staff: Punch In (Work ON)
@app.post("/staff/punch-in")
def punch_in(staff_id: str, location_address: str, db: Session = Depends(get_db)):
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    new_entry = Attendance(
        staff_id=staff_id,
        date=today_str,
        punch_in_time=datetime.datetime.now(),
        punch_in_location=location_address,
        status="ON"
    )
    db.add(new_entry)
    db.commit()
    return {"status": "success", "message": "Work ON registered!"}

# Staff: Punch Out (Work OFF + Photo Upload)
@app.post("/staff/punch-out")
def punch_out(
    staff_id: str = Form(...),
    location_address: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    record = db.query(Attendance).filter(
        Attendance.staff_id == staff_id,
        Attendance.date == today_str,
        Attendance.status == "ON"
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="No active Punch-In record found for today!")

    # File save logic
    file_extension = os.path.splitext(photo.filename)[1]
    safe_filename = f"{staff_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    record.punch_out_time = datetime.datetime.now()
    record.punch_out_location = location_address
    record.work_photo_url = f"/uploads/{safe_filename}"
    record.status = "COMPLETED"

    db.commit()
    return {"status": "success", "message": "Work OFF registered with photo!", "photo_url": record.work_photo_url}

# Admin: Today Report
@app.get("/admin/today-report")
def get_today_report(db: Session = Depends(get_db)):
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    records = db.query(Attendance).filter(Attendance.date == today_str).all()
    return {"date": today_str, "records": records}