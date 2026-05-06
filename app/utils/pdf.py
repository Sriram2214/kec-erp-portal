import os
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.platypus import Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Resolve absolute path to institutional header
# We check the root for local development first, then fallback to static for Vercel
_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR   = os.path.abspath(os.path.join(_UTILS_DIR, '..'))
_ROOT      = os.path.abspath(os.path.join(_APP_DIR, '..'))

LOCAL_HEADER = os.path.join(_ROOT, 'Header2.jpg.jpeg')
STATIC_HEADER = os.path.join(_APP_DIR, 'static', 'header.png')

HEADER_IMG = LOCAL_HEADER if os.path.exists(LOCAL_HEADER) else STATIC_HEADER
LOGO_PATH  = os.path.join(_APP_DIR, 'static', 'logo.png')

NAVY = colors.HexColor('#1a2a5e')

def get_institutional_header(story, page_w):
    """
    Insert the official KEC letterhead image as the PDF header.
    FALLBACK REMOVED: If the image is missing, this will fail intentionally
    to ensure the user knows their branding file is missing.
    """
    if os.path.exists(HEADER_IMG):
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(HEADER_IMG)
            iw, ih = img.getSize()
            aspect = iw / ih
            img_h = page_w / aspect
            story.append(RLImage(HEADER_IMG, width=page_w, height=img_h))
            story.append(Paragraph('<font size=6 color=grey>v1.1 - Branded</font>', styles['Normal']))
            story.append(Spacer(1, 1*mm))
            return True
        except Exception as e:
            import logging
            logging.error(f"HEADER LOAD ERROR: {e} at {HEADER_IMG}")
            pass
    else:
        import logging
        logging.error(f"HEADER NOT FOUND at {HEADER_IMG}")
    
    # ERROR CASE: Image exists but failed to load or does not exist
    import logging
    err_msg = f"STILL OLD VERSION? [DEBUG] Institutional Branding Missing.\nPath: {HEADER_IMG}"
    logging.error(err_msg)
    
    styles = getSampleStyleSheet()
    err_para = Paragraph(
        f'<font color="red"><b>{err_msg}</b></font>',
        styles['Normal']
    )
    story.append(err_para)
    story.append(Spacer(1, 10*mm))
    return False
