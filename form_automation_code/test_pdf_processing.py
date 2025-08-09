#!/usr/bin/env python3

import sys
import os
sys.path.append('/app/backend')

from server import parse_personal_data, fill_pdf_form, PersonalData

def test_pdf_processing():
    """Test the PDF processing functionality."""
    
    # Test data
    raw_data = """Last Name: ALSQOUR
First Name: NAEL OMAR MOHAMMAD
Middle Name: [Leave Blank]
Current Address: 3100 Van Buren Blvd Apt 611, Riverside, CA 92503
Mobile Phone: +1 (832) 757-3013
Driver's License #: W9493684
Position Applying For: Driver
Salary Desired: $20/hour
College: University in Jordan
Field of Study: Business/General
Degree: Bachelor's
Year Received: 2008
Languages Speak: Arabic, English
License Type: Driver License
License Number: W9493684
State: CA
Expiration: 11/20/2028"""

    print("=== Testing Data Parsing ===")
    try:
        parsed_data = parse_personal_data(raw_data)
        print(f"✓ Parsed data successfully")
        print(f"  First Name: {parsed_data.first_name}")
        print(f"  Last Name: {parsed_data.last_name}")
        print(f"  Position: {parsed_data.position_applying}")
        print(f"  Salary: {parsed_data.salary_desired}")
    except Exception as e:
        print(f"✗ Error parsing data: {e}")
        return False

    print(f"\n=== Testing PDF Form Filling ===")
    pdf_path = "/app/content.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"✗ PDF file not found: {pdf_path}")
        return False
    
    try:
        filled_pdf_path = fill_pdf_form(pdf_path, parsed_data)
        print(f"✓ PDF filled successfully: {filled_pdf_path}")
        
        if os.path.exists(filled_pdf_path):
            print(f"✓ Output file created: {os.path.getsize(filled_pdf_path)} bytes")
            return True
        else:
            print(f"✗ Output file not created")
            return False
            
    except Exception as e:
        print(f"✗ Error filling PDF: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_processing()
    if success:
        print(f"\n🎉 All tests passed!")
    else:
        print(f"\n❌ Some tests failed!")
    
    sys.exit(0 if success else 1)