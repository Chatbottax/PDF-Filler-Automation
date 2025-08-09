#!/usr/bin/env python3

import fitz  # PyMuPDF
import pdfplumber
import json
from pathlib import Path

def examine_pdf_with_pymupdf(pdf_path):
    """Examine PDF using PyMuPDF to detect form fields and text."""
    print("=== Examining PDF with PyMuPDF ===")
    
    doc = fitz.open(pdf_path)
    
    # Basic document info
    print(f"Document info:")
    print(f"  Pages: {len(doc)}")
    print(f"  Title: {doc.metadata.get('title', 'N/A')}")
    print(f"  Author: {doc.metadata.get('author', 'N/A')}")
    
    # Check for form fields
    print(f"\n=== Form Fields Analysis ===")
    has_form_fields = False
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get form fields (widgets)
        widgets = list(page.widgets())
        if widgets:
            has_form_fields = True
            print(f"\nPage {page_num + 1} has {len(widgets)} form field(s):")
            
            for i, widget in enumerate(widgets):
                print(f"  Field {i+1}:")
                print(f"    Type: {widget.field_type_string}")
                print(f"    Name: {widget.field_name}")
                print(f"    Label: {widget.field_label}")
                print(f"    Value: {widget.field_value}")
                print(f"    Rect: {widget.rect}")
                print(f"    Flags: {widget.field_flags}")
    
    if not has_form_fields:
        print("No interactive form fields detected in PDF")
        
    # Extract all text to understand content
    print(f"\n=== Text Content Analysis ===")
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        if text.strip():
            print(f"\nPage {page_num + 1} text preview (first 500 chars):")
            print(text[:500] + "..." if len(text) > 500 else text)
            
            # Look for common form patterns
            form_indicators = [
                'name:', 'address:', 'phone:', 'email:', 'date:',
                'signature:', 'employer:', 'position:', 'salary:',
                'license:', 'experience:', 'education:', 'skills:',
                '____', '___', 'first name', 'last name', 'middle',
                'application', 'form', 'employment', 'personal'
            ]
            
            found_indicators = []
            text_lower = text.lower()
            for indicator in form_indicators:
                if indicator in text_lower:
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"  Form indicators found: {found_indicators}")
    
    doc.close()
    return has_form_fields

def examine_pdf_with_pdfplumber(pdf_path):
    """Examine PDF using pdfplumber for detailed text extraction."""
    print(f"\n=== Examining PDF with pdfplumber ===")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Document has {len(pdf.pages)} pages")
        
        for i, page in enumerate(pdf.pages):
            print(f"\nPage {i+1} analysis:")
            
            # Extract text with positions
            chars = page.chars
            print(f"  Total characters: {len(chars)}")
            
            # Extract lines and possible form fields
            lines = page.extract_text().split('\n') if page.extract_text() else []
            print(f"  Text lines: {len(lines)}")
            
            # Look for potential fillable areas (lines, underscores, etc.)
            potential_fields = []
            for line_num, line in enumerate(lines):
                line = line.strip()
                if line:
                    # Look for patterns that suggest form fields
                    if ('____' in line or 
                        line.endswith(':') or 
                        'name' in line.lower() or
                        'address' in line.lower() or
                        'phone' in line.lower() or
                        'email' in line.lower() or
                        'date' in line.lower()):
                        potential_fields.append((line_num, line))
            
            if potential_fields:
                print(f"  Potential form fields found:")
                for line_num, field in potential_fields[:10]:  # Show first 10
                    print(f"    Line {line_num}: {field}")
            
            # Check for tables (structured data)
            tables = page.extract_tables()
            if tables:
                print(f"  Tables found: {len(tables)}")
                for j, table in enumerate(tables):
                    print(f"    Table {j+1}: {len(table)} rows, {len(table[0]) if table else 0} columns")

def main():
    pdf_path = "/app/content.pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        return
        
    print(f"Examining PDF: {pdf_path}")
    
    # Examine with both libraries
    has_form_fields = examine_pdf_with_pymupdf(pdf_path)
    examine_pdf_with_pdfplumber(pdf_path)
    
    print(f"\n=== Summary ===")
    if has_form_fields:
        print("✅ PDF contains interactive form fields - can be filled programmatically")
    else:
        print("📝 PDF appears to be a static document - will need OCR-based field detection")

if __name__ == "__main__":
    main()