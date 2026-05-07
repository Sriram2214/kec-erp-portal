import os
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.platypus import Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Resolve absolute path to institutional header
_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR   = os.path.abspath(os.path.join(_UTILS_DIR, '..'))
_ROOT      = os.path.abspath(os.path.join(_APP_DIR, '..'))

# Primary path (should be in static folder for Vercel/Production)
STATIC_HEADER = os.path.join(_APP_DIR, 'static', 'header.png')
# Local override if you have the file in the root
LOCAL_HEADER  = os.path.join(_ROOT, 'Header2.jpg.jpeg')

# Prefer the static one as it is tracked in Git
HEADER_IMG = STATIC_HEADER if os.path.exists(STATIC_HEADER) else LOCAL_HEADER
LOGO_PATH  = os.path.join(_APP_DIR, 'static', 'logo.png')

NAVY = colors.HexColor('#1a2a5e')

def get_institutional_header(story, page_w):
    """
    Insert the official KEC letterhead image as the PDF header.
    """
    if os.path.exists(HEADER_IMG):
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(HEADER_IMG)
            iw, ih = img.getSize()
            aspect = iw / ih
            img_h = page_w / aspect
            story.append(RLImage(HEADER_IMG, width=page_w, height=img_h))
            story.append(Spacer(1, 2*mm))
            return True
        except Exception as e:
            import logging
            logging.error(f"HEADER LOAD ERROR: {e} at {HEADER_IMG}")
            pass

    # Clean Fallback (No debug text, just the professional look)
    styles = getSampleStyleSheet()
    hdr_center = Paragraph(
        '<b>KINGS ENGINEERING COLLEGE</b><br/>'
        '<font size=8><b>AN AUTONOMOUS INSTITUTION</b></font><br/>'
        '<font size=7>ACCREDITED WITH NAAC AND AFFILIATED TO ANNA UNIVERSITY</font><br/>'
        '<font size=7>Chennai-Bangalore Highway, Irungattukottai, Sriperumbudur, Chennai – 602 117.</font><br/>'
        '<font size=7>Ph.: 044 – 71224401 -08. Fax: 044 – 71224410</font>',
        ParagraphStyle('HDR_C', fontName='Helvetica-Bold', fontSize=16, textColor=NAVY, alignment=TA_CENTER, leading=16)
    )
    story.append(hdr_center)
    story.append(Spacer(1, 2*mm))
    return False
