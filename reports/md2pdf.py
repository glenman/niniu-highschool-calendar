#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown to PDF converter with Chinese support
"""

import markdown
import sys
from weasyprint import HTML, CSS

def md_to_pdf(md_file, pdf_file):
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc']
    )
    
    # Create full HTML with styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                font-size: 22pt;
                color: #1a1a1a;
                border-bottom: 3px solid #2563eb;
                padding-bottom: 10px;
                margin-top: 30px;
                margin-bottom: 20px;
            }}
            h2 {{
                font-size: 18pt;
                color: #1e40af;
                margin-top: 25px;
                margin-bottom: 15px;
                border-left: 4px solid #2563eb;
                padding-left: 10px;
            }}
            h3 {{
                font-size: 14pt;
                color: #1e3a8a;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
            h4 {{
                font-size: 12pt;
                color: #1e40af;
                margin-top: 15px;
                margin-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 10pt;
            }}
            th {{
                background-color: #2563eb;
                color: white;
                padding: 8px;
                text-align: left;
                font-weight: bold;
            }}
            td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }}
            tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            blockquote {{
                border-left: 4px solid #3b82f6;
                margin: 15px 0;
                padding: 10px 20px;
                background-color: #eff6ff;
                color: #1e40af;
            }}
            strong {{
                color: #dc2626;
                font-weight: bold;
            }}
            hr {{
                border: none;
                border-top: 2px solid #e5e7eb;
                margin: 25px 0;
            }}
            ul, ol {{
                margin: 10px 0;
                padding-left: 25px;
            }}
            li {{
                margin: 5px 0;
            }}
            code {{
                background-color: #f1f5f9;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: "Monaco", "Consolas", monospace;
                font-size: 10pt;
            }}
            p {{
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    HTML(string=full_html).write_pdf(pdf_file)
    print(f"PDF generated: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 md2pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    
    md_to_pdf(sys.argv[1], sys.argv[2])
