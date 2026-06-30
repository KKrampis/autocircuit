#!/usr/bin/env python3
"""Convert PAPER_DRAFT.md to a styled academic PDF using reportlab."""
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib import colors

INPUT = "/Users/anish/Desktop/aisc_project/PAPER_DRAFT.md"
OUTPUT = "/Users/anish/Desktop/aisc_project/PAPER_DRAFT.pdf"

# --- Styles ---
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'AcademicTitle', parent=styles['Title'],
    fontName='Times-Bold', fontSize=20, leading=26,
    alignment=TA_CENTER, spaceAfter=12,
)
author_style = ParagraphStyle(
    'Author', parent=styles['Normal'],
    fontName='Times-Roman', fontSize=12, leading=16,
    alignment=TA_CENTER, spaceAfter=6,
)
abstract_style = ParagraphStyle(
    'Abstract', parent=styles['Normal'],
    fontName='Times-Italic', fontSize=10, leading=14,
    alignment=TA_JUSTIFY, leftIndent=36, rightIndent=36,
    spaceAfter=12, spaceBefore=6,
)
h1_style = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName='Times-Bold', fontSize=14, leading=18,
    spaceBefore=18, spaceAfter=8, textColor=HexColor('#1a1a1a'),
)
h2_style = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName='Times-Bold', fontSize=12, leading=16,
    spaceBefore=14, spaceAfter=6, textColor=HexColor('#2a2a2a'),
)
h3_style = ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontName='Times-BoldItalic', fontSize=11, leading=14,
    spaceBefore=10, spaceAfter=4, textColor=HexColor('#333333'),
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName='Times-Roman', fontSize=10, leading=13,
    alignment=TA_JUSTIFY, spaceAfter=6,
)
bullet_style = ParagraphStyle(
    'Bullet', parent=body_style,
    leftIndent=24, bulletIndent=12, spaceAfter=3,
)
numbered_style = ParagraphStyle(
    'Numbered', parent=body_style,
    leftIndent=24, bulletIndent=12, spaceAfter=3,
)
table_cell_style = ParagraphStyle(
    'TableCell', parent=styles['Normal'],
    fontName='Times-Roman', fontSize=8, leading=10,
)
table_header_style = ParagraphStyle(
    'TableHeader', parent=styles['Normal'],
    fontName='Times-Bold', fontSize=8, leading=10,
)

def clean_md(text):
    """Clean markdown formatting for reportlab Paragraph XML."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Escaped pipes in tables
    text = text.replace(r'\_', '_')
    # Links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Clean ampersands and angle brackets for XML FIRST
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    # Now apply markup (after escaping)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" size="9">\1</font>', text)
    return text

def parse_table(lines):
    """Parse markdown table lines into a reportlab Table."""
    rows = []
    for line in lines:
        line = line.strip().strip('|')
        cells = [c.strip() for c in line.split('|')]
        rows.append(cells)

    if len(rows) < 2:
        return None

    # Remove separator row (----)
    data_rows = [rows[0]]
    for row in rows[1:]:
        if all(re.match(r'^[-:]+$', c) for c in row):
            continue
        data_rows.append(row)

    if not data_rows:
        return None

    # Convert to Paragraph objects
    table_data = []
    for i, row in enumerate(data_rows):
        style = table_header_style if i == 0 else table_cell_style
        table_data.append([Paragraph(clean_md(c), style) for c in row])

    ncols = max(len(r) for r in table_data)
    # Pad short rows
    for row in table_data:
        while len(row) < ncols:
            row.append(Paragraph('', table_cell_style))

    avail_width = letter[0] - 2 * inch
    col_width = avail_width / ncols

    t = Table(table_data, colWidths=[col_width] * ncols)
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8e8e8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t

def build_pdf():
    with open(INPUT, 'r') as f:
        lines = f.readlines()

    doc = SimpleDocTemplate(
        OUTPUT, pagesize=letter,
        leftMargin=1*inch, rightMargin=1*inch,
        topMargin=1*inch, bottomMargin=1*inch,
    )

    story = []
    i = 0
    in_abstract = False
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i].rstrip('\n')

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End code block — render as a simple table cell with monospace font
                safe_lines = []
                for l in code_lines:
                    l = l.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    safe_lines.append(l)
                code_text = '\n'.join(safe_lines)
                from reportlab.platypus import Preformatted
                code_style = ParagraphStyle(
                    'Code', parent=body_style,
                    fontName='Courier', fontSize=7, leading=9,
                    leftIndent=18, spaceBefore=4, spaceAfter=4,
                )
                story.append(Preformatted(code_text, code_style))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Title (# )
        if line.startswith('# ') and not line.startswith('## '):
            story.append(Spacer(1, 72))
            story.append(Paragraph(clean_md(line[2:].strip()), title_style))
            story.append(Spacer(1, 24))
            i += 1
            continue

        # H1 (## )
        if line.startswith('## ') and not line.startswith('### '):
            heading_text = line[3:].strip()
            if heading_text == 'Abstract':
                in_abstract = True
                story.append(Paragraph('Abstract', h1_style))
                i += 1
                continue
            else:
                in_abstract = False
            story.append(Paragraph(clean_md(heading_text), h1_style))
            i += 1
            continue

        # H2 (### )
        if line.startswith('### ') and not line.startswith('#### '):
            in_abstract = False
            story.append(Paragraph(clean_md(line[4:].strip()), h2_style))
            i += 1
            continue

        # H3 (#### )
        if line.startswith('#### '):
            story.append(Paragraph(clean_md(line[5:].strip()), h3_style))
            i += 1
            continue

        # Horizontal rule
        if line.strip() == '---':
            story.append(Spacer(1, 8))
            i += 1
            continue

        # Table detection
        if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
            table_lines = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                table_lines.append(lines[i].rstrip('\n'))
                i += 1
            t = parse_table(table_lines)
            if t:
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 4))
            continue

        # Bullet points
        if line.strip().startswith('- '):
            text = line.strip()[2:]
            story.append(Paragraph(clean_md(text), bullet_style, bulletText='•'))
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.+)', line.strip())
        if m:
            num, text = m.groups()
            story.append(Paragraph(clean_md(text), numbered_style, bulletText=f'{num}.'))
            i += 1
            continue

        # Empty line
        if not line.strip():
            i += 1
            continue

        # Regular paragraph - collect continuation lines
        para_lines = [line]
        while i + 1 < len(lines):
            next_line = lines[i + 1].rstrip('\n')
            if (not next_line.strip() or next_line.startswith('#') or
                next_line.startswith('- ') or next_line.strip().startswith('|') or
                next_line.strip() == '---' or next_line.strip().startswith('```') or
                re.match(r'^\d+\.\s+', next_line.strip())):
                break
            para_lines.append(next_line)
            i += 1

        full_text = ' '.join(l.strip() for l in para_lines)
        style = abstract_style if in_abstract else body_style
        story.append(Paragraph(clean_md(full_text), style))
        i += 1

    doc.build(story)
    print(f"PDF written to {OUTPUT}")

if __name__ == '__main__':
    build_pdf()
