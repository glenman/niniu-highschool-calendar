#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown to PDF converter using fpdf2 with Chinese support
"""

from fpdf import FPDF
import re
import sys

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Add Chinese font - use system font
        self.add_font("STHeiti", "", "/System/Library/Fonts/STHeiti Medium.ttc")
        
    def header(self):
        pass
    
    def footer(self):
        self.set_y(-15)
        self.set_font("STHeiti", size=8)
        self.set_text_color(128)
        self.cell(0, 10, f'第 {self.page_no()} 页', 0, 0, 'C')

def parse_markdown_to_pdf(md_file, pdf_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            i += 1
            continue
        
        # H1
        if line.startswith('# '):
            pdf.set_font("STHeiti", size=18)
            pdf.set_text_color(26, 26, 26)
            pdf.ln(5)
            pdf.multi_cell(0, 10, line[2:].strip())
            pdf.set_draw_color(37, 99, 235)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
        
        # H2
        elif line.startswith('## '):
            pdf.ln(5)
            pdf.set_font("STHeiti", size=14)
            pdf.set_text_color(30, 64, 175)
            pdf.multi_cell(0, 8, line[3:].strip())
            pdf.ln(3)
        
        # H3
        elif line.startswith('### '):
            pdf.ln(3)
            pdf.set_font("STHeiti", size=12)
            pdf.set_text_color(30, 58, 138)
            pdf.multi_cell(0, 7, line[4:].strip())
            pdf.ln(2)
        
        # H4
        elif line.startswith('#### '):
            pdf.ln(2)
            pdf.set_font("STHeiti", size=11)
            pdf.set_text_color(30, 64, 175)
            pdf.multi_cell(0, 6, line[5:].strip())
            pdf.ln(2)
        
        # HR
        elif line.strip() == '---':
            pdf.ln(3)
            pdf.set_draw_color(229, 231, 235)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
        
        # Blockquote
        elif line.startswith('> '):
            pdf.set_fill_color(239, 246, 255)
            pdf.set_text_color(30, 64, 175)
            pdf.set_font("STHeiti", size=10)
            text = line[2:].strip()
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            pdf.multi_cell(0, 6, f"  {text}", fill=True)
            pdf.set_text_color(51, 51, 51)
            pdf.ln(2)
        
        # Table
        elif '|' in line and line.strip().startswith('|'):
            # Collect table lines
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            i -= 1  # Back up one
            
            if len(table_lines) > 1:
                # Parse table
                pdf.set_font("STHeiti", size=9)
                headers = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]
                data_rows = []
                for tline in table_lines[2:]:  # Skip separator
                    cells = [cell.strip() for cell in tline.split('|')[1:-1]]
                    data_rows.append(cells)
                
                # Calculate column widths
                num_cols = len(headers)
                col_width = 190 / num_cols
                
                # Draw header
                pdf.set_fill_color(37, 99, 235)
                pdf.set_text_color(255, 255, 255)
                for header in headers:
                    # Remove markdown formatting
                    header = re.sub(r'\*\*(.*?)\*\*', r'\1', header)
                    pdf.cell(col_width, 7, header[:20], 1, 0, 'C', True)
                pdf.ln()
                
                # Draw data rows
                pdf.set_text_color(51, 51, 51)
                for row_idx, row in enumerate(data_rows):
                    if row_idx % 2 == 1:
                        pdf.set_fill_color(248, 250, 252)
                        fill = True
                    else:
                        fill = False
                    
                    for cell in row:
                        # Remove markdown formatting
                        cell = re.sub(r'\*\*(.*?)\*\*', r'\1', cell)
                        pdf.cell(col_width, 6, cell[:25], 1, 0, 'L', fill)
                    pdf.ln()
                
                pdf.ln(3)
        
        # List items
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            pdf.set_font("STHeiti", size=10)
            pdf.set_text_color(51, 51, 51)
            text = line.strip()[2:]
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            pdf.cell(5)
            pdf.multi_cell(0, 6, f"• {text}")
        
        # Numbered list
        elif re.match(r'^\d+\.', line.strip()):
            pdf.set_font("STHeiti", size=10)
            pdf.set_text_color(51, 51, 51)
            text = line.strip()
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            pdf.cell(5)
            pdf.multi_cell(0, 6, text)
        
        # Bold text line
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            pdf.set_font("STHeiti", size=10)
            pdf.set_text_color(220, 38, 38)
            text = line.strip()[2:-2]
            pdf.multi_cell(0, 6, text)
            pdf.set_text_color(51, 51, 51)
        
        # Regular paragraph
        else:
            pdf.set_font("STHeiti", size=10)
            pdf.set_text_color(51, 51, 51)
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            if text.strip():
                pdf.multi_cell(0, 6, text.strip())
        
        i += 1
    
    pdf.output(pdf_file)
    print(f"PDF generated: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 md2pdf_simple.py <input.md> <output.pdf>")
        sys.exit(1)
    
    parse_markdown_to_pdf(sys.argv[1], sys.argv[2])
