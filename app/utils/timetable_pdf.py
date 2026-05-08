import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from app.utils.pdf import get_institutional_header

def generate_timetable_pdf(schedules):
    """
    Generate a professional Institutional Examination Timetable PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    # 1. Header
    get_institutional_header(story, 480)
    story.append(Spacer(1, 10))

    # 2. Title
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=16, 
        alignment=TA_CENTER, spaceAfter=20, fontName='Helvetica-Bold'
    )
    story.append(Paragraph("END SEMESTER THEORY EXAMINATIONS - TIMETABLE", title_style))

    # 3. Table Data
    data = [['S.No', 'Exam Date', 'Course Code', 'Course Title', 'Session', 'Venue']]
    
    # Sort schedules by date and session
    sorted_s = sorted(schedules, key=lambda x: (x.exam_date, x.session))
    
    for idx, s in enumerate(sorted_s, 1):
        data.append([
            str(idx),
            s.exam_date.strftime('%d-%m-%Y'),
            s.course.course_code,
            s.course.course_title,
            s.session,
            s.venue or 'Main Hall'
        ])

    # 4. Table Styling
    t = Table(data, colWidths=[30, 75, 80, 200, 50, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2a5e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'), # Left align course title
    ]))
    
    story.append(t)
    story.append(Spacer(1, 30))

    # 5. Footer Signature
    sign_style = ParagraphStyle('SignStyle', fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')
    story.append(Spacer(1, 40))
    story.append(Paragraph("Controller of Examinations", sign_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
