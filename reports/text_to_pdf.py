#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple text to PDF converter with basic formatting
"""

from fpdf import FPDF
import sys
import re

class ChinesePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Heiti", "", "/System/Library/Fonts/STHeiti Medium.ttc")
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Heiti", size=8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'- {self.page_no()} -', 0, 0, 'C')

def clean_text(text):
    """Remove markdown formatting"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
    text = re.sub(r'`(.+?)`', r'\1', text)  # Code
    return text

def md_to_pdf(md_file, pdf_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    pdf = ChinesePDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    for line in lines:
        line = line.rstrip()
        
        # Empty line
        if not line:
            pdf.ln(3)
            continue
        
        # HR
        if line == '---':
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(2)
            continue
        
        # H1
        if line.startswith('# '):
            pdf.ln(5)
            pdf.set_font("Heiti", size=16)
            pdf.set_text_color(0, 0, 0)
            text = clean_text(line[2:])
            pdf.multi_cell(0, 8, text)
            pdf.set_draw_color(37, 99, 235)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
            pdf.ln(4)
            continue
        
        # H2
        if line.startswith('## '):
            pdf.ln(4)
            pdf.set_font("Heiti", size=13)
            pdf.set_text_color(30, 64, 175)
            text = clean_text(line[3:])
            pdf.multi_cell(0, 7, text)
            pdf.ln(2)
            continue
        
        # H3
        if line.startswith('### '):
            pdf.ln(3)
            pdf.set_font("Heiti", size=11)
            pdf.set_text_color(30, 58, 138)
            text = clean_text(line[4:])
            pdf.multi_cell(0, 6, text)
            pdf.ln(2)
            continue
        
        # H4
        if line.startswith('#### '):
            pdf.ln(2)
            pdf.set_font("Heiti", size=10)
            pdf.set_text_color(30, 64, 175)
            text = clean_text(line[5:])
            pdf.multi_cell(0, 6, text)
            pdf.ln(1)
            continue
        
        # Blockquote
        if line.startswith('> '):
            pdf.set_font("Heiti", size=10)
            pdf.set_text_color(30, 64, 175)
            text = clean_text(line[2:])
            pdf.set_x(15)
            pdf.multi_cell(180, 5, text)
            pdf.set_text_color(51, 51, 51)
            continue
        
        # List
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            pdf.set_font("Heiti", size=10)
            pdf.set_text_color(51, 51, 51)
            text = clean_text(line.strip()[2:])
            pdf.set_x(15)
            pdf.multi_cell(180, 5, '• ' + text)
            continue
        
        # Numbered list
        if re.match(r'^\s*\d+\.', line):
            pdf.set_font("Heiti", size=10)
            pdf.set_text_color(51, 51, 51)
            text = clean_text(line.strip())
            pdf.set_x(15)
            pdf.multi_cell(180, 5, text)
            continue
        
        # Table - simplified handling
        if '|' in line:
            pdf.set_font("Heiti", size=9)
            pdf.set_text_color(51, 51, 51)
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells and not all(c.replace('-', '').replace(':', '') == '' for c in cells):
                text = '  |  '.join(cells)
                text = clean_text(text)
                pdf.multi_cell(0, 5, text)
            continue
        
        # Regular text
        pdf.set_font("Heiti", size=10)
        pdf.set_text_color(51, 51, 51)
        text = clean_text(line)
        pdf.multi_cell(0, 5, text)
    
    pdf.output(pdf_file)
    print(f"✅ PDF已生成: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python3 text_to_pdf.py <输入.md> <输出.pdf>")
        sys.exit(1)
    
    md_to_pdf(sys.argv[1], sys.argv[2])
