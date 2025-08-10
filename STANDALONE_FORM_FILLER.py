#!/usr/bin/env python3
"""
STANDALONE PDF & Word Form Filler for SAMIA
Runs on your local computer - NO URLS NEEDED
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import fitz  # PyMuPDF
from docx import Document
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
import uuid
import os
import webbrowser
import threading
import time
import sys

app = FastAPI()

# NAEL'S DATA - BUILT IN
NAEL_DATA = """Last Name: ALSQOUR
First Name: NAEL OMAR MOHAMMAD
Middle Name: [Leave Blank]
Other Names Used: [Leave Blank]
Current Address: 3100 Van Buren Blvd Apt 611, Riverside, CA 92503
Home Phone: [Leave Blank]
Mobile Phone: +1 (832) 757-3013
Email: [Leave Blank]
Driver's License #: W9493684
How did you hear about us?: Friend referral
Worked at company before?: No
Relatives working here?: No
Proof of right to work in U.S.: Yes
Are you 18 or older?: Yes
Terminated before?: No
Can work any shift?: Yes
Can work overtime/weekends?: Yes
Position Applying For: Driver
Salary Desired: $20/hour
Special Skills/Training: College educated in Jordan; fluent in Arabic & English; proficient in Word; experienced with Uber, Lyft, DoorDash, student transportation apps
College: University in Jordan
Field of Study: Business/General
Degree: Bachelor's
Year Received: 2008
Other Skills: Transportation apps, navigation, rideshare & delivery platforms
Languages Speak: Arabic, English
Languages Read: Arabic, English
Languages Write: Arabic, English
License Type: Driver License
License Number: W9493684
State: CA
Expiration: 11/20/2028
CPR/BLS Certified: No
Employer #1: Upland Furniture LLC, 735 S Cactus Ave, Upland, CA 91786 — From 09/01/2024 to 09/30/2024 — Full-Time — May Contact: Yes — Supervisor: N/A — Position: Delivery Driver — Reason: Left for higher pay in apps
Employer #2: Self-Employed – Uber, Lyft, DoorDash, Student Transportation — From 10/2024 to Present — Full-Time — Position: Passenger transport, rideshare, deliveries — Reason: Current"""

def parse_personal_data(raw_data: str) -> dict:
    """Parse raw text input into structured data."""
    lines = raw_data.strip().split('\n')
    data = {}
    
    for line in lines:
        line = line.strip()
        if not line or ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip().lower()
        value = value.strip()
        
        # Map to standardized keys
        if 'last name' in key:
            data['last_name'] = value
        elif 'first name' in key:
            data['first_name'] = value
        elif 'middle name' in key:
            data['middle_name'] = value if value not in ['[Leave Blank]', ''] else ''
        elif 'current address' in key:
            data['current_address'] = value
        elif 'mobile phone' in key:
            data['mobile_phone'] = value
        elif 'email' in key:
            data['email'] = value if value not in ['[Leave Blank]', ''] else ''
        elif 'driver' in key and 'license' in key:
            data['drivers_license'] = value
        elif 'position' in key:
            data['position_applying'] = value
        elif 'salary' in key:
            data['salary_desired'] = value
        elif 'college' in key:
            data['college_name'] = value
        elif 'field of study' in key:
            data['field_of_study'] = value
        elif 'degree' in key:
            data['degree'] = value
        elif 'year received' in key:
            data['year_received'] = value
        elif 'languages speak' in key:
            data['languages_speak'] = value
        elif 'languages read' in key:
            data['languages_read'] = value
        elif 'languages write' in key:
            data['languages_write'] = value
        elif 'license type' in key:
            data['license_type'] = value
        elif 'license number' in key:
            data['license_number'] = value
        elif 'license state' in key or key == 'state':
            data['license_state'] = value
        elif 'expiration' in key:
            data['license_expiration'] = value
        elif 'skills' in key or 'training' in key:
            data['special_skills'] = value
        elif 'employer #1' in key:
            data['employer1_name'] = value
        elif 'employer #2' in key:
            data['employer2_name'] = value
    
    return data

def fill_pdf_form(pdf_path: str, data: dict) -> tuple[str, list]:
    """Fill PDF form with personal data."""
    doc = fitz.open(pdf_path)
    report = []
    
    # Name parsing
    full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
    first_name_parts = data.get('first_name', '').split()
    first_name_only = first_name_parts[0] if first_name_parts else data.get('first_name', '')
    
    # Field mapping - CORRECTED FOR NAME ISSUE
    field_mapping = {
        'Name legal': data.get('last_name', ''),  # Last name only
        'rst': first_name_only,  # First name only
        'F': data.get('first_name', ''),  # Full first name
        'Middle': data.get('middle_name', ''),
        'Your Current Address': data.get('current_address', ''),
        'Mobile Phone': data.get('mobile_phone', ''),
        'Email': data.get('email', ''),
        'Drivers License': data.get('drivers_license', ''),
        'Last Name First Name': full_name,
        'Last Name First Name_2': full_name,
        'Last Name First Name_3': full_name,
        'Position Applying for': data.get('position_applying', ''),
        'Salary desired': data.get('salary_desired', ''),
        'Name and LocationCollege': data.get('college_name', ''),
        'Field of StudyCollege': data.get('field_of_study', ''),
        'DegreeCertificate AwardedCollege': data.get('degree', ''),
        'Year ReceivedCollege': data.get('year_received', ''),
        'Other Skills Relevant to Position please specify': data.get('special_skills', ''),
        'LANGUAGES Speak': data.get('languages_speak', ''),
        'Read': data.get('languages_read', ''),
        'Write': data.get('languages_write', ''),
        'Type': data.get('license_type', ''),
        'No_3': data.get('license_number', ''),
        'State': data.get('license_state', ''),
        'Exp': data.get('license_expiration', ''),
        'Employer Name and Address': data.get('employer1_name', ''),
        'Employer Name and Address May we contact Yes No': data.get('employer2_name', ''),
        'Date': datetime.now().strftime('%m/%d/%Y'),
    }
    
    filled_count = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = list(page.widgets())
        
        for widget in widgets:
            field_name = widget.field_name
            field_value = field_mapping.get(field_name, "")
            
            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT and field_value:
                try:
                    widget.field_value = str(field_value)
                    widget.update()
                    filled_count += 1
                    report.append(f"✅ {field_name}: {field_value}")
                except Exception as e:
                    report.append(f"❌ Failed to fill '{field_name}': {str(e)}")
    
    # Save to D:\Completed Docs
    output_dir = Path("D:/Completed Docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"FILLED_FORM_{timestamp}.pdf"
    output_path = output_dir / filename
    
    doc.save(str(output_path))
    doc.close()
    
    report.append(f"📁 Saved to: {output_path}")
    return str(output_path), report

@app.get("/")
async def home():
    """Main form interface."""
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>SAMIA's Form Filler - STANDALONE</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; }}
        .form-group {{ margin: 20px 0; }}
        label {{ display: block; font-weight: bold; margin-bottom: 5px; }}
        input[type="file"] {{ width: 100%; padding: 10px; border: 2px dashed #ccc; border-radius: 5px; }}
        textarea {{ width: 100%; height: 300px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-family: monospace; font-size: 12px; }}
        button {{ background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin: 10px 5px; }}
        button:hover {{ background: #0056b3; }}
        .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .report {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; margin: 10px 0; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }}
        .status {{ background: #e7f3ff; border: 1px solid #bee5eb; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 SAMIA's Standalone Form Filler</h1>
        <div class="status">
            <strong>✅ Running on your computer - No internet URLs needed!</strong><br>
            Files save directly to: <strong>D:\\Completed Docs</strong>
        </div>
        
        <form id="formFiller" enctype="multipart/form-data">
            <div class="form-group">
                <label>1. Select PDF or Word Document:</label>
                <input type="file" id="fileInput" accept=".pdf,.doc,.docx" required>
            </div>
            
            <div class="form-group">
                <label>2. Personal Data:</label>
                <button type="button" onclick="loadNaelData()">Load Nael's Data</button>
                <button type="button" onclick="clearData()">Clear</button>
                <textarea id="dataInput" placeholder="Paste personal information here...">{NAEL_DATA}</textarea>
            </div>
            
            <button type="submit">Fill Form & Save to D:\\Completed Docs</button>
        </form>
        
        <div id="result"></div>
    </div>

    <script>
        const naelData = `{NAEL_DATA}`;
        
        function loadNaelData() {{
            document.getElementById('dataInput').value = naelData;
        }}
        
        function clearData() {{
            document.getElementById('dataInput').value = '';
        }}

        document.getElementById('formFiller').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const resultDiv = document.getElementById('result');
            const fileInput = document.getElementById('fileInput');
            const dataInput = document.getElementById('dataInput');
            
            if (!fileInput.files[0]) {{
                resultDiv.innerHTML = '<div class="error">❌ Please select a file</div>';
                return;
            }}
            
            if (!dataInput.value.trim()) {{
                resultDiv.innerHTML = '<div class="error">❌ Please enter personal data</div>';
                return;
            }}
            
            resultDiv.innerHTML = '<div>🔄 Processing form...</div>';
            
            try {{
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('data', dataInput.value);
                
                const response = await fetch('/fill-form', {{
                    method: 'POST',
                    body: formData
                }});
                
                if (!response.ok) {{
                    const errorText = await response.text();
                    throw new Error(`Error: ${{response.status}} - ${{errorText}}`);
                }}
                
                const result = await response.json();
                
                let reportHtml = '<div class="success">✅ <strong>Form processed successfully!</strong></div>';
                reportHtml += '<div class="report">';
                result.report.forEach(item => {{
                    reportHtml += `<div>${{item}}</div>`;
                }});
                reportHtml += '</div>';
                
                resultDiv.innerHTML = reportHtml;
                
            }} catch (error) {{
                resultDiv.innerHTML = `<div class="error">❌ ${{error.message}}</div>`;
            }}
        }});
    </script>
</body>
</html>'''
    return HTMLResponse(content=html)

@app.post("/fill-form")
async def fill_form_endpoint(file: UploadFile = File(...), data: str = Form(...)):
    """Fill form and save to local drive."""
    try:
        # Save uploaded file temporarily
        temp_dir = Path(tempfile.gettempdir())
        temp_input = temp_dir / f"input_{uuid.uuid4()}{Path(file.filename).suffix}"
        
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse data
        parsed_data = parse_personal_data(data)
        
        # Process PDF
        if temp_input.suffix.lower() == '.pdf':
            output_path, report = fill_pdf_form(str(temp_input), parsed_data)
        else:
            # For Word docs, you could add Word processing here
            raise HTTPException(status_code=400, detail="Only PDF files supported in this version")
        
        # Clean up
        temp_input.unlink(missing_ok=True)
        
        return {"success": True, "output_path": output_path, "report": report}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def open_browser():
    """Open browser after server starts."""
    time.sleep(1)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STARTING SAMIA'S STANDALONE FORM FILLER")
    print("=" * 60)
    print("✅ Server starting at: http://localhost:8000")
    print("✅ Files will save to: D:\\Completed Docs")
    print("✅ Browser will open automatically...")
    print("=" * 60)
    
    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")