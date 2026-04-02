#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Markdown to PDF using reportlab
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import re
import sys

# Register Chinese font
pdfmetrics.registerFont(TTFont('Heiti', '/System/Library/Fonts/STHeiti Medium.ttc'))

def clean_markdown(text):
    """Remove markdown formatting"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text

def md_to_pdf(md_file, pdf_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4
    
    # Margins
    left_margin = 2 * cm
    right_margin = 2 * cm
    top_margin = 2.5 * cm
    bottom_margin = 2 * cm
    
    # Text width
    text_width = width - left_margin - right_margin
    
    # Current position
    y = height - top_margin
    page_num = 1
    
    def new_page():
        nonlocal y, page_num
        c.showPage()
        y = height - top_margin
        page_num += 1
        # Draw page number
        c.setFont('Heiti', 9)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawCentredString(width / 2, 1 * cm, f'- {page_num} -')
        y = height - top_margin
    
    def check_space(needed):
        nonlocal y
        if y < bottom_margin + needed:
            new_page()
    
    for line in lines:
        line = line.rstrip()
        
        # Empty line
        if not line:
            y -= 0.3 * cm
            continue
        
        # HR
        if line == '---':
            check_space(0.5 * cm)
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.line(left_margin, y, width - right_margin, y)
            y -= 0.5 * cm
            continue
        
        # H1
        if line.startswith('# '):
            check_space(1.5 * cm)
            y -= 0.3 * cm
            c.setFont('Heiti', 16)
            c.setFillColorRGB(0, 0, 0)
            text = clean_markdown(line[2:])
            c.drawString(left_margin, y, text)
            y -= 0.2 * cm
            c.setStrokeColorRGB(0.145, 0.388, 0.922)
            c.setLineWidth(2)
            c.line(left_margin, y, left_margin + len(text) * 0.4 * cm, y)
            y -= 0.8 * cm
            continue
        
        # H2
        if line.startswith('## '):
            check_space(1 * cm)
            y -= 0.2 * cm
            c.setFont('Heiti', 13)
            c.setFillColorRGB(0.118, 0.251, 0.686)
            text = clean_markdown(line[3:])
            c.drawString(left_margin, y, text)
            y -= 0.6 * cm
            continue
        
        # H3
        if line.startswith('### '):
            check_space(0.8 * cm)
            c.setFont('Heiti', 11)
            c.setFillColorRGB(0.118, 0.227, 0.541)
            text = clean_markdown(line[4:])
            c.drawString(left_margin, y, text)
            y -= 0.5 * cm
            continue
        
        # H4
        if line.startswith('#### '):
            check_space(0.6 * cm)
            c.setFont('Heiti', 10)
            c.setFillColorRGB(0.118, 0.251, 0.686)
            text = clean_markdown(line[5:])
            c.drawString(left_margin, y, text)
            y -= 0.5 * cm
            continue
        
        # Blockquote
        if line.startswith('> '):
            check_space(0.5 * cm)
            c.setFont('Heiti', 10)
            c.setFillColorRGB(0.118, 0.251, 0.686)
            text = clean_markdown(line[2:])
            c.drawString(left_margin + 0.5 * cm, y, text)
            y -= 0.5 * cm
            continue
        
        # List items
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            check_space(0.5 * cm)
            c.setFont('Heiti', 10)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            text = clean_markdown(line.strip()[2:])
            c.drawString(left_margin + 0.5 * cm, y, '• ' + text)
            y -= 0.5 * cm
            continue
        
        # Numbered list
        if re.match(r'^\s*\d+\.', line):
            check_space(0.5 * cm)
            c.setFont('Heiti', 10)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            text = clean_markdown(line.strip())
            c.drawString(left_margin + 0.5 * cm, y, text)
            y -= 0.5 * cm
            continue
        
        # Table - simplified
        if '|' in line:
            check_space(0.5 * cm)
            c.setFont('Heiti', 9)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells and not all(c.replace('-', '').replace(':', '') == '' for c in cells):
                text = '  |  '.join(cells)
                text = clean_markdown(text)
                c.drawString(left_margin, y, text)
                y -= 0.5 * cm
            continue
        
        # Regular text
        check_space(0.5 * cm)
        c.setFont('Heiti', 10)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        text = clean_markdown(line)
        c.drawString(left_margin, y, text)
        y -= 0.5 * cm
    
    c.save()
    print(f"✅ PDF已生成: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python3 simple_reportlab.py <输入.md> <输出.pdf>")
        sys.exit(1)
    
    md_to_pdf(sys.argv[1], sys.argv[2])
