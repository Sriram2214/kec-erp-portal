import pandas as pd
import os
import logging
from sqlalchemy import text
from app import create_app, db
from app.models import Course, Department

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_courses_from_excel(file_path):
    app = create_app()
    with app.app_context():
        # 1. Database Schema Update (Raw SQL for Postgres)
        try:
            # Add batch column if not exists
            db.session.execute(text("ALTER TABLE course ADD COLUMN IF NOT EXISTS batch VARCHAR(20)"))
            # Increase department column length
            db.session.execute(text("ALTER TABLE course ALTER COLUMN department TYPE VARCHAR(200)"))
            
            # Try to drop the old unique constraint on course_code
            # In Postgres it might be course_course_code_key
            try:
                db.session.execute(text("ALTER TABLE course DROP CONSTRAINT IF EXISTS course_course_code_key"))
            except Exception as e:
                logger.warning(f"Could not drop course_course_code_key: {e}")

            # Also try the one Flask-SQLAlchemy might have generated
            try:
                db.session.execute(text("ALTER TABLE course DROP CONSTRAINT IF EXISTS uq_course_course_code"))
            except Exception as e:
                pass
                
            db.session.commit()
            logger.info("Database schema updated successfully.")
        except Exception as e:
            logger.error(f"Error updating schema: {e}")
            db.session.rollback()

        # 2. Read Excel
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return

        # Fetch valid dept codes from DB
        dept_codes = [d.code for d in Department.query.all()]

        logger.info(f"Reading Excel file: {file_path}")
        df = pd.read_excel(file_path)
        
        # Clean column names (strip whitespace)
        df.columns = [c.strip() for c in df.columns]
        
        added = 0
        updated = 0
        
        for index, row in df.iterrows():
            batch = str(row['BATCH']).strip()
            regulation = str(row['REGULATION']).strip()
            raw_dept = str(row['DEPARTMENT']).strip().upper()
            sem = int(row['SEM'])
            code = str(row['COURSE CODE']).strip()
            title = str(row['COURSE NAME']).strip()
            credits = int(row['CREDITS'])

            # Map department
            dept = raw_dept
            if 'COMPUTER SCIENCE AND ENGINEERING' in raw_dept and 'ARTIFICIAL' not in raw_dept: dept = 'CSE'
            elif 'ELECTRONICS AND COMMUNICATION' in raw_dept: dept = 'ECE'
            elif 'INFORMATION TECHNOLOGY' in raw_dept: dept = 'IT'
            elif 'MECHANICAL' in raw_dept: dept = 'MECH'
            elif 'DATA SCIENCE' in raw_dept: dept = 'AI&DS'
            elif 'MACHINE LEARNING' in raw_dept: dept = 'AIML'
            elif 'BIOMEDICAL' in raw_dept: dept = 'BME'
            elif 'ROBOTICS' in raw_dept: dept = 'RAA'
            elif 'CSE' in raw_dept: dept = 'CSE'
            elif 'ECE' in raw_dept: dept = 'ECE'
            elif 'MECH' in raw_dept: dept = 'MECH'
            elif 'BME' in raw_dept: dept = 'BME'
            elif 'AIDS' in raw_dept or 'AI&DS' in raw_dept: dept = 'AI&DS'
            
            # Fallback: if it's still long, just take the first word if it matches a code
            if dept not in dept_codes:
                for dc in dept_codes:
                    if dc in raw_dept:
                        dept = dc
                        break
            
            is_lab = 'LAB' in title.upper() or 'PRACTICAL' in title.upper() or 'WORKSHOP' in title.upper()

            # Check if exists
            existing = Course.query.filter_by(
                course_code=code,
                department=dept,
                batch=batch
            ).first()

            if existing:
                existing.course_title = title
                existing.credits = credits
                existing.semester = sem
                existing.regulation = regulation
                existing.is_lab = is_lab
                updated += 1
            else:
                new_course = Course(
                    course_code=code,
                    course_title=title,
                    department=dept,
                    batch=batch,
                    credits=credits,
                    semester=sem,
                    regulation=regulation,
                    is_lab=is_lab
                )
                db.session.add(new_course)
                added += 1

            # Commit in batches of 100
            if (added + updated) % 100 == 0:
                db.session.commit()
                logger.info(f"Processed {added + updated} rows...")

        db.session.commit()
        logger.info(f"Done! Added {added} courses, updated {updated} courses.")

if __name__ == "__main__":
    excel_file = "COURSE DETAIL - 2021 TO 2025.xlsx"
    seed_courses_from_excel(excel_file)
