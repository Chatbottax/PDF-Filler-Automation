#!/usr/bin/env python3

import fitz
from pathlib import Path

def get_all_field_names():
    """Get actual field names from the PDF"""
    pdf_path = "/app/content.pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF not found: {pdf_path}")
        return
    
    doc = fitz.open(pdf_path)
    print("=== ALL PDF FIELD NAMES ===")
    
    all_fields = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        widgets = list(page.widgets())
        
        if widgets:
            print(f"\nPage {page_num + 1}:")
            for widget in widgets:
                field_name = widget.field_name
                field_type = widget.field_type_string
                all_fields.append(field_name)
                print(f"  '{field_name}' | Type: {field_type}")
    
    doc.close()
    
    print(f"\n=== TOTAL FIELDS: {len(all_fields)} ===")
    return all_fields

if __name__ == "__main__":
    get_all_field_names()