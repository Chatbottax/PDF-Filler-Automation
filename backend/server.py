from fastapi import FastAPI, APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import fitz  # PyMuPDF
import tempfile
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import json
import threading

# Global storage for temporary file sessions
file_sessions = {}


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class PersonalData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    last_name: str = ""
    first_name: str = ""
    middle_name: str = ""
    other_names: str = ""
    current_address: str = ""
    home_phone: str = ""
    mobile_phone: str = ""
    email: str = ""
    drivers_license: str = ""
    how_heard_about_us: str = ""
    worked_before: str = "No"
    relatives_working: str = "No"
    right_to_work: str = "Yes"
    age_18_or_older: str = "Yes"
    terminated_before: str = "No"
    can_work_any_shift: str = "Yes"
    can_work_overtime: str = "Yes"
    position_applying: str = ""
    salary_desired: str = ""
    special_skills: str = ""
    
    # Education
    college_name: str = ""
    field_of_study: str = ""
    degree: str = ""
    year_received: str = ""
    
    # Languages
    languages_speak: str = ""
    languages_read: str = ""
    languages_write: str = ""
    
    # License info
    license_type: str = ""
    license_number: str = ""
    license_state: str = ""
    license_expiration: str = ""
    cpr_bls_certified: str = "No"
    
    # Employment History
    employer1_name: str = ""
    employer1_dates_from: str = ""
    employer1_dates_to: str = ""
    employer1_full_time: str = ""
    employer1_contact: str = ""
    employer1_supervisor: str = ""
    employer1_position: str = ""
    employer1_reason_leaving: str = ""
    
    employer2_name: str = ""
    employer2_dates_from: str = ""
    employer2_dates_to: str = ""
    employer2_full_time: str = ""
    employer2_contact: str = ""
    employer2_supervisor: str = ""
    employer2_position: str = ""
    employer2_reason_leaving: str = ""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PersonalDataCreate(BaseModel):
    raw_data: str  # Raw text input from user

class EmailRequest(BaseModel):
    recipient_email: str
    subject: str = "Completed Form"
    message: str = "Please find the completed form attached."
    session_id: str


# Data parsing function
def parse_personal_data(raw_data: str) -> PersonalData:
    """Parse raw text input into structured personal data."""
    lines = raw_data.strip().split('\n')
    data = PersonalData()
    
    for line in lines:
        line = line.strip()
        if not line or ':' not in line:
            continue
            
        key, value = line.split(':', 1)
        key = key.strip().lower()
        value = value.strip()
        
        # Map input data to PersonalData fields
        if 'last name' in key:
            data.last_name = value
        elif 'first name' in key:
            data.first_name = value
        elif 'middle name' in key:
            data.middle_name = value
        elif 'other names' in key:
            data.other_names = value
        elif 'current address' in key:
            data.current_address = value
        elif 'home phone' in key:
            data.home_phone = value
        elif 'mobile phone' in key:
            data.mobile_phone = value
        elif 'email' in key:
            data.email = value
        elif 'driver' in key and 'license' in key:
            data.drivers_license = value
        elif 'how did you hear' in key:
            data.how_heard_about_us = value
        elif 'worked at company' in key or 'worked before' in key:
            data.worked_before = value
        elif 'relatives' in key:
            data.relatives_working = value
        elif 'right to work' in key:
            data.right_to_work = value
        elif '18 or older' in key:
            data.age_18_or_older = value
        elif 'terminated' in key:
            data.terminated_before = value
        elif 'any shift' in key:
            data.can_work_any_shift = value
        elif 'overtime' in key or 'weekend' in key:
            data.can_work_overtime = value
        elif 'position' in key:
            data.position_applying = value
        elif 'salary' in key:
            data.salary_desired = value
        elif 'skills' in key or 'training' in key:
            data.special_skills = value
        elif 'college' in key:
            data.college_name = value
        elif 'field of study' in key:
            data.field_of_study = value
        elif 'degree' in key:
            data.degree = value
        elif 'year received' in key:
            data.year_received = value
        elif 'languages' in key and 'speak' in key:
            data.languages_speak = value
        elif 'languages' in key and 'read' in key:
            data.languages_read = value
        elif 'languages' in key and 'write' in key:
            data.languages_write = value
        elif 'license type' in key:
            data.license_type = value
        elif 'license number' in key:
            data.license_number = value
        elif 'license state' in key or 'state' in key:
            data.license_state = value
        elif 'expiration' in key:
            data.license_expiration = value
        elif 'cpr' in key or 'bls' in key:
            data.cpr_bls_certified = value
        elif 'employer #1' in key or 'employer 1' in key:
            data.employer1_name = value
        elif 'employer #2' in key or 'employer 2' in key:
            data.employer2_name = value
    
    return data


def fill_pdf_form(pdf_path: str, personal_data: PersonalData) -> str:
    """Fill PDF form fields with personal data."""
    doc = fitz.open(pdf_path)
    
    # Create field mapping
    field_mapping = {
        # Personal Information
        'Name legal': personal_data.first_name,
        'rst': personal_data.last_name,
        'F': personal_data.first_name,
        'Middle': personal_data.middle_name,
        'Other names under which you have worked or used for educational purposes': personal_data.other_names,
        'Your Current Address': personal_data.current_address,
        'Home Phone': personal_data.home_phone,
        'Mobile Phone': personal_data.mobile_phone,
        'Email': personal_data.email,
        'Drivers License': personal_data.drivers_license,
        "Driver's License": personal_data.drivers_license,
        
        # Employment desired
        'Position Applying for': personal_data.position_applying,
        'Salary desired': personal_data.salary_desired,
        
        # Education
        'Name and LocationCollege': personal_data.college_name,
        'Field of StudyCollege': personal_data.field_of_study,
        'DegreeCertificate AwardedCollege': personal_data.degree,
        'Year ReceivedCollege': personal_data.year_received,
        
        # Skills
        'Other Skills Relevant to Position please specify': personal_data.special_skills,
        
        # Languages
        'LANGUAGES Speak': personal_data.languages_speak,
        'Read': personal_data.languages_read,
        'Write': personal_data.languages_write,
        
        # License Information
        'Type': personal_data.license_type,
        'No': personal_data.license_number,
        'State': personal_data.license_state,
        'Exp': personal_data.license_expiration,
        
        # Employment History
        'Employer Name and Address': personal_data.employer1_name,
        'Indicate Month and year From': personal_data.employer1_dates_from,
        'To': personal_data.employer1_dates_to,
        'Supervisors Name Title': personal_data.employer1_supervisor,
        'Position TitleJob Duties': personal_data.employer1_position,
        'Reason For Leaving': personal_data.employer1_reason_leaving,
        
        # Second employer
        'Employer Name and Address_2': personal_data.employer2_name,
        'Indicate Month and year From_2': personal_data.employer2_dates_from,
        'To_2': personal_data.employer2_dates_to,
        'Position TitleJob Duties_2': personal_data.employer2_position,
        'Reason For Leaving_2': personal_data.employer2_reason_leaving,
    }
    
    # Fill form fields
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = list(page.widgets())
        
        for widget in widgets:
            field_name = widget.field_name
            field_value = field_mapping.get(field_name, "")
            
            if field_value and widget.field_type in (fitz.PDF_WIDGET_TYPE_TEXT,):
                widget.field_value = str(field_value)
                widget.update()
    
    # Save filled PDF
    output_path = f"/tmp/filled_form_{uuid.uuid4()}.pdf"
    doc.save(output_path)
    doc.close()
    
    return output_path


# API Routes
@api_router.get("/")
async def root():
    return {"message": "PDF Form Filler API"}

@api_router.post("/parse-data")
async def parse_data(request: PersonalDataCreate):
    """Parse raw personal data text into structured format."""
    try:
        parsed_data = parse_personal_data(request.raw_data)
        return {"success": True, "data": parsed_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing data: {str(e)}")

@api_router.post("/fill-form")
async def fill_form(
    file: UploadFile = File(...),
    data: str = Form(...)
):
    """Fill PDF form with provided data."""
    try:
        # Parse personal data
        parsed_data = parse_personal_data(data)
        
        # Save uploaded file temporarily
        temp_input = f"/tmp/input_{uuid.uuid4()}.pdf"
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Fill the form
        filled_pdf_path = fill_pdf_form(temp_input, parsed_data)
        
        # Generate session ID for email functionality
        session_id = str(uuid.uuid4())
        
        # Store file path for potential email sending
        file_sessions[session_id] = {
            'file_path': filled_pdf_path,
            'timestamp': datetime.utcnow(),
            'original_filename': file.filename
        }
        
        # Clean up input file
        os.unlink(temp_input)
        
        # Generate filename
        filename = f"filled_form_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        response = FileResponse(
            filled_pdf_path,
            media_type='application/pdf',
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "X-Session-ID": session_id  # Send session ID to frontend
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error filling form: {str(e)}")

@api_router.post("/send-email")
async def send_email(request: EmailRequest):
    """Send filled PDF via email."""
    try:
        # Get file path from session
        session_info = file_sessions.get(request.session_id)
        if not session_info:
            raise HTTPException(status_code=400, detail="Invalid session ID or file expired")
        
        file_path = session_info['file_path']
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="File not found")
        
        # Configure email settings
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        sender_email = os.environ.get('SENDER_EMAIL', '')
        sender_password = os.environ.get('SENDER_PASSWORD', '')
        
        if not sender_email or not sender_password or sender_email == "demo@example.com":
            raise HTTPException(
                status_code=400, 
                detail="Email configuration not set. Please configure SENDER_EMAIL and SENDER_PASSWORD in the backend .env file."
            )
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = request.recipient_email
        msg['Subject'] = request.subject
        
        # Add body
        msg.attach(MIMEText(request.message, 'plain'))
        
        # Add attachment
        with open(file_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename=completed_form.pdf'
            )
            msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, request.recipient_email, text)
        server.quit()
        
        return {"success": True, "message": "Email sent successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error sending email: {str(e)}")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()