#!/usr/bin/env python3
"""
PDF Form Filler for SAMIA
Simple local script that fills PDF forms and saves to D:\Completed Docs
"""

import fitz  # PyMuPDF
from pathlib import Path
import sys
from datetime import datetime

# NAEL'S PERSONAL DATA
PERSONAL_DATA = {
    'last_name': 'ALSQOUR',
    'first_name': 'NAEL OMAR MOHAMMAD',
    'middle_name': '',
    'other_names': '',
    'current_address': '3100 Van Buren Blvd Apt 611, Riverside, CA 92503',
    'home_phone': '',
    'mobile_phone': '+1 (832) 757-3013',
    'email': '',
    'drivers_license': 'W9493684',
    'how_heard_about_us': 'Friend referral',
    'worked_before': 'No',
    'relatives_working': 'No',
    'right_to_work': 'Yes',
    'age_18_or_older': 'Yes',
    'terminated_before': 'No',
    'can_work_any_shift': 'Yes',
    'can_work_overtime': 'Yes',
    'position_applying': 'Driver',
    'salary_desired': '$20/hour',
    'special_skills': 'College educated in Jordan; fluent in Arabic & English; proficient in Word; experienced with Uber, Lyft, DoorDash, student transportation apps',
    'college_name': 'University in Jordan',
    'field_of_study': 'Business/General',
    'degree': 'Bachelor\'s',
    'year_received': '2008',
    'languages_speak': 'Arabic, English',
    'languages_read': 'Arabic, English',
    'languages_write': 'Arabic, English',
    'license_type': 'Driver License',
    'license_number': 'W9493684',
    'license_state': 'CA',
    'license_expiration': '11/20/2028',
    'cpr_bls_certified': 'No',
    'employer1_name': 'Upland Furniture LLC, 735 S Cactus Ave, Upland, CA 91786',
    'employer1_dates_from': '09/01/2024',
    'employer1_dates_to': '09/30/2024',
    'employer1_supervisor': 'N/A',
    'employer1_position': 'Delivery Driver',
    'employer1_reason_leaving': 'Left for higher pay in apps',
    'employer2_name': 'Self-Employed – Uber, Lyft, DoorDash, Student Transportation',
    'employer2_dates_from': '10/2024',
    'employer2_dates_to': 'Present',
    'employer2_position': 'Passenger transport, rideshare, deliveries',
    'employer2_reason_leaving': 'Current'
}

def fill_pdf_form(input_pdf_path, output_pdf_path):
    """Fill PDF form with Nael's data and save to specified location."""
    
    if not Path(input_pdf_path).exists():
        print(f"❌ ERROR: Input PDF not found: {input_pdf_path}")
        return False
    
    try:
        # Open the PDF
        doc = fitz.open(input_pdf_path)
        print(f"✅ Opened PDF: {input_pdf_path}")
        
        # Field mapping based on actual PDF field names
        field_mapping = {
            # Page 1 - Personal Information
            'Name legal': PERSONAL_DATA['last_name'],
            'rst': PERSONAL_DATA['first_name'], 
            'F': PERSONAL_DATA['first_name'],
            'Middle': PERSONAL_DATA['middle_name'],
            'Other names under which you have worked or used for educational purposes': PERSONAL_DATA['other_names'],
            'Your Current Address': PERSONAL_DATA['current_address'],
            'Home Phone': PERSONAL_DATA['home_phone'],
            'Mobile Phone': PERSONAL_DATA['mobile_phone'],
            'Email': PERSONAL_DATA['email'],
            'Drivers License': PERSONAL_DATA['drivers_license'],
            'Employee': PERSONAL_DATA['how_heard_about_us'],
            
            # Page 2 - Position and Education  
            'Last Name First Name': f"{PERSONAL_DATA['first_name']} {PERSONAL_DATA['last_name']}",
            'Position Applying for': PERSONAL_DATA['position_applying'],
            'Salary desired': PERSONAL_DATA['salary_desired'],
            
            # Education
            'Name and LocationCollege': PERSONAL_DATA['college_name'],
            'Field of StudyCollege': PERSONAL_DATA['field_of_study'],
            'DegreeCertificate AwardedCollege': PERSONAL_DATA['degree'],
            'Year ReceivedCollege': PERSONAL_DATA['year_received'],
            
            # Skills
            'Other Skills Relevant to Position please specify': PERSONAL_DATA['special_skills'],
            
            # Languages
            'LANGUAGES Speak': PERSONAL_DATA['languages_speak'],
            'Read': PERSONAL_DATA['languages_read'],
            'Write': PERSONAL_DATA['languages_write'],
            
            # License Information
            'Type': PERSONAL_DATA['license_type'],
            'No_3': PERSONAL_DATA['license_number'],
            'State': PERSONAL_DATA['license_state'],
            'Exp': PERSONAL_DATA['license_expiration'],
            
            # Page 3 - Employment History
            'Last Name First Name_2': f"{PERSONAL_DATA['first_name']} {PERSONAL_DATA['last_name']}",
            'Employer Name and Address': PERSONAL_DATA['employer1_name'],
            'Indicate Month and year From': PERSONAL_DATA['employer1_dates_from'],
            'To': PERSONAL_DATA['employer1_dates_to'],
            'Supervisors Name Title': PERSONAL_DATA['employer1_supervisor'],
            'Position TitleJob Duties': PERSONAL_DATA['employer1_position'],
            'Reason For Leaving': PERSONAL_DATA['employer1_reason_leaving'],
            
            # Second employer
            'Employer Name and Address May we contact Yes No': PERSONAL_DATA['employer2_name'],
            'Indicate Month and year From_2': PERSONAL_DATA['employer2_dates_from'],
            'To_2': PERSONAL_DATA['employer2_dates_to'],
            'Position TitleJob Duties_2': PERSONAL_DATA['employer2_position'],
            'Reason For Leaving_2': PERSONAL_DATA['employer2_reason_leaving'],
            
            # Page 4 - Signature
            'Last Name First Name_3': f"{PERSONAL_DATA['first_name']} {PERSONAL_DATA['last_name']}",
            'Date': datetime.now().strftime('%m/%d/%Y'),
        }
        
        # Fill form fields
        filled_count = 0
        total_fields = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            total_fields += len(widgets)
            
            for widget in widgets:
                field_name = widget.field_name
                field_value = field_mapping.get(field_name, "")
                
                if field_value and widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                    widget.field_value = str(field_value)
                    widget.update()
                    filled_count += 1
        
        # Save the filled PDF
        doc.save(output_pdf_path)
        doc.close()
        
        print(f"✅ SUCCESS: Filled {filled_count} fields out of {total_fields} total fields")
        print(f"✅ SAVED TO: {output_pdf_path}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    """Main function to fill PDF forms."""
    
    print("=" * 60)
    print("PDF FORM FILLER FOR NAEL ALSQOUR")
    print("=" * 60)
    
    # Get input PDF path
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]
    else:
        input_pdf = input("Enter path to PDF form (or drag and drop): ").strip().strip('"')
    
    if not input_pdf:
        print("❌ No PDF file specified")
        input("Press Enter to exit...")
        return
    
    # Create output path in D:\Completed Docs
    input_path = Path(input_pdf)
    output_dir = Path("D:/Completed Docs")
    
    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"FILLED_{input_path.stem}_{timestamp}.pdf"
    output_path = output_dir / output_filename
    
    print(f"📁 Input:  {input_pdf}")
    print(f"📁 Output: {output_path}")
    print()
    
    # Fill the PDF
    success = fill_pdf_form(input_pdf, str(output_path))
    
    if success:
        print()
        print("🎉 COMPLETED SUCCESSFULLY! 🎉")
        print(f"✅ Your filled form is saved at: {output_path}")
        print("✅ Ready to submit!")
    else:
        print()
        print("❌ FAILED TO FILL FORM")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()