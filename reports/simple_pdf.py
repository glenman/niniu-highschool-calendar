#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Markdown to PDF converter using fpdf2
"""

from fpdf import FPDF
import sys

def md_to_pdf(md_file, pdf_file):
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Add Chinese font
    pdf.add_font("Heiti", "", "/System/Library/Fonts/STHeiti Medium.ttc")
    
    # Write markdown with fpdf2's markdown support
    pdf.set_font("Heiti", size=11)
    pdf.write_markdown(content)
    
    # Save PDF
    pdf.output(pdf_file)
    print(f"PDF generated: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 simple_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    
    md_to_pdf(sys.argv[1], sys.argv[2])
