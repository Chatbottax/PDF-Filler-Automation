#!/usr/bin/env python3
"""
FIXED PDF Form Filler for SAMIA
This version fixes all the bugs in the previous code
"""

import fitz  # PyMuPDF
from pathlib import Path
import sys
from datetime import datetime

def fill_pdf_form(input_pdf_path, output_pdf_path):
    """Fill PDF form with Nael's data - FIXED VERSION."""
    
    if not Path(input_pdf_path).exists():
        print(f"❌ ERROR: Input PDF not found: {input_pdf_path}")
        return False
    
    try:
        # Open the PDF
        doc = fitz.open(input_pdf_path)
        print(f"✅ Opened PDF: {input_pdf_path}")
        print(f"✅ Pages: {len(doc)}")
        
        # NAEL'S DATA - FIXED AND COMPLETE
        data = {
            'last_name': 'ALSQOUR',
            'first_name': 'NAEL OMAR MOHAMMAD',
            'address': '3100 Van Buren Blvd Apt 611, Riverside, CA 92503',
            'mobile': '+1 (832) 757-3013',
            'license': 'W9493684',
            'position': 'Driver',
            'salary': '$20/hour',
            'college': 'University in Jordan',
            'degree': 'Bachelor',
            'field_study': 'Business/General',
            'year': '2008',
            'skills': 'College educated in Jordan; fluent in Arabic & English; proficient in Word; experienced with Uber, Lyft, DoorDash, student transportation apps',
            'languages': 'Arabic, English',
            'license_type': 'Driver License',
            'license_state': 'CA',
            'license_exp': '11/20/2028',
            'employer1': 'Upland Furniture LLC, 735 S Cactus Ave, Upland, CA 91786',
            'emp1_from': '09/01/2024',
            'emp1_to': '09/30/2024',
            'emp1_position': 'Delivery Driver',
            'emp1_reason': 'Left for higher pay in apps',
            'employer2': 'Self-Employed – Uber, Lyft, DoorDash, Student Transportation',
            'emp2_from': '10/2024',
            'emp2_to': 'Present',
            'emp2_position': 'Passenger transport, rideshare, deliveries',
            'emp2_reason': 'Current',
            'today': datetime.now().strftime('%m/%d/%Y')
        }
        
        # Fill ALL form fields - this is the FIXED approach
        filled_count = 0
        total_fields = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            print(f"Page {page_num + 1}: {len(widgets)} fields")
            
            for widget in widgets:
                total_fields += 1
                field_name = widget.field_name
                field_type = widget.field_type
                
                # FIXED: Only fill text fields
                if field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                    
                    # FIXED: Smart field matching based on field name content
                    field_lower = field_name.lower()
                    value_to_fill = ""
                    
                    # Name fields
                    if 'last name' in field_lower or field_name == 'Name legal':
                        value_to_fill = data['last_name']
                    elif 'first name' in field_lower or field_name in ['rst', 'F']:
                        value_to_fill = data['first_name']
                    elif field_name == 'Middle':
                        value_to_fill = ""  # Leave blank as requested
                    elif 'last name first name' in field_lower:
                        value_to_fill = f"{data['first_name']} {data['last_name']}"
                    
                    # Contact info
                    elif 'address' in field_lower:
                        value_to_fill = data['address']
                    elif 'mobile' in field_lower:
                        value_to_fill = data['mobile']
                    elif 'drivers license' in field_lower or 'drivers license' in field_name:
                        value_to_fill = data['license']
                    
                    # Position and salary
                    elif 'position applying' in field_lower:
                        value_to_fill = data['position']
                    elif 'salary desired' in field_lower:
                        value_to_fill = data['salary']
                    
                    # Education
                    elif 'college' in field_lower and 'location' in field_lower:
                        value_to_fill = data['college']
                    elif 'field of study' in field_lower and 'college' in field_lower:
                        value_to_fill = data['field_study']
                    elif 'degree' in field_lower and 'college' in field_lower:
                        value_to_fill = data['degree']
                    elif 'year received' in field_lower and 'college' in field_lower:
                        value_to_fill = data['year']
                    
                    # Skills and languages
                    elif 'skills relevant' in field_lower:
                        value_to_fill = data['skills']
                    elif field_name == 'LANGUAGES Speak' or (field_name == 'Read' or field_name == 'Write'):
                        value_to_fill = data['languages']
                    
                    # License details
                    elif field_name == 'Type':
                        value_to_fill = data['license_type']
                    elif field_name == 'No_3':
                        value_to_fill = data['license']
                    elif field_name == 'State':
                        value_to_fill = data['license_state']
                    elif field_name == 'Exp':
                        value_to_fill = data['license_exp']
                    
                    # Employment history
                    elif 'employer name and address' in field_lower and not '2' in field_name:
                        value_to_fill = data['employer1']
                    elif 'month and year from' in field_lower and not '2' in field_name:
                        value_to_fill = data['emp1_from']
                    elif field_name == 'To':
                        value_to_fill = data['emp1_to']
                    elif 'position title' in field_lower and not '2' in field_name:
                        value_to_fill = data['emp1_position']
                    elif 'reason for leaving' in field_lower and not '2' in field_name:
                        value_to_fill = data['emp1_reason']
                    
                    # Second employer
                    elif 'employer name' in field_lower and ('2' in field_name or 'may we contact' in field_lower):
                        value_to_fill = data['employer2']
                    elif 'from_2' in field_name:
                        value_to_fill = data['emp2_from']
                    elif 'to_2' in field_name:
                        value_to_fill = data['emp2_to']
                    elif 'position title' in field_lower and '2' in field_name:
                        value_to_fill = data['emp2_position']
                    elif 'reason for leaving' in field_lower and '2' in field_name:
                        value_to_fill = data['emp2_reason']
                    
                    # Date field
                    elif field_name == 'Date':
                        value_to_fill = data['today']
                    
                    # Fill the field if we have a value
                    if value_to_fill:
                        try:
                            widget.field_value = str(value_to_fill)
                            widget.update()
                            filled_count += 1
                            print(f"  ✅ Filled: {field_name} = {value_to_fill}")
                        except Exception as e:
                            print(f"  ❌ Failed to fill {field_name}: {e}")
                    else:
                        print(f"  ⚪ Skipped: {field_name} (no matching data)")
        
        # FIXED: Ensure output directory exists
        output_path_obj = Path(output_pdf_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the filled PDF
        doc.save(output_pdf_path)
        doc.close()
        
        print(f"\n✅ SUCCESS: Filled {filled_count} fields out of {total_fields} total fields")
        print(f"✅ SAVED TO: {output_pdf_path}")
        
        # FIXED: Verify the file was actually created and has content
        if Path(output_pdf_path).exists():
            file_size = Path(output_pdf_path).stat().st_size
            print(f"✅ File size: {file_size:,} bytes")
            return True
        else:
            print("❌ ERROR: Output file was not created")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function - FIXED VERSION."""
    
    print("=" * 60)
    print("FIXED PDF FORM FILLER FOR NAEL ALSQOUR")
    print("=" * 60)
    
    # Get input PDF path
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]
    else:
        print("Drag and drop a PDF file onto this script, or enter the path:")
        input_pdf = input("PDF file path: ").strip().strip('"')
    
    if not input_pdf:
        print("❌ No PDF file specified")
        input("Press Enter to exit...")
        return
    
    # FIXED: Better path handling
    input_path = Path(input_pdf)
    if not input_path.exists():
        print(f"❌ PDF file not found: {input_pdf}")
        input("Press Enter to exit...")
        return
    
    # FIXED: Ensure D:\Completed Docs exists
    output_dir = Path("D:/Completed Docs")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Output directory ready: {output_dir}")
    except Exception as e:
        print(f"❌ Cannot create output directory: {e}")
        output_dir = Path.cwd()  # Fallback to current directory
        print(f"📁 Using current directory instead: {output_dir}")
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"FILLED_{input_path.stem}_{timestamp}.pdf"
    output_path = output_dir / output_filename
    
    print(f"\n📁 Input:  {input_pdf}")
    print(f"📁 Output: {output_path}")
    print()
    
    # Fill the PDF
    success = fill_pdf_form(str(input_path), str(output_path))
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 COMPLETED SUCCESSFULLY! 🎉")
        print(f"✅ Your filled form is saved at:")
        print(f"   {output_path}")
        print("✅ Ready to submit!")
        print("=" * 60)
    else:
        print("\n❌ FAILED TO FILL FORM - Check errors above")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()