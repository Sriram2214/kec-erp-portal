import pandas as pd
import os
import logging
from sqlalchemy import text
from app import create_app, db
from app.models import Course, Department, Degree, Batch, Regulation, Curriculum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_courses_from_excel(file_path):
    app = create_app()
    with app.app_context():
        logger.info("Starting course seed process...")

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
        
        from app.models import Batch, Regulation, Curriculum
        
        for index, row in df.iterrows():
            batch_label = str(row['BATCH']).strip()
            reg_name = str(row['REGULATION']).strip()
            raw_dept = str(row['DEPARTMENT']).strip().upper()
            sem = int(row['SEM'])
            code = str(row['COURSE CODE']).strip()
            title = str(row['COURSE NAME']).strip()
            credits = int(row['CREDITS'])

            # Map department
            dept_code = raw_dept
            if 'COMPUTER SCIENCE AND ENGINEERING' in raw_dept and 'ARTIFICIAL' not in raw_dept: dept_code = 'CSE'
            elif 'ELECTRONICS AND COMMUNICATION' in raw_dept: dept_code = 'ECE'
            elif 'INFORMATION TECHNOLOGY' in raw_dept: dept_code = 'IT'
            elif 'MECHANICAL' in raw_dept: dept_code = 'MECH'
            elif 'DATA SCIENCE' in raw_dept: dept_code = 'AI&DS'
            elif 'MACHINE LEARNING' in raw_dept: dept_code = 'AIML'
            elif 'BIOMEDICAL' in raw_dept: dept_code = 'BME'
            elif 'ROBOTICS' in raw_dept: dept_code = 'RAA'
            elif 'CSE' in raw_dept: dept_code = 'CSE'
            elif 'ECE' in raw_dept: dept_code = 'ECE'
            elif 'MECH' in raw_dept: dept_code = 'MECH'
            elif 'BME' in raw_dept: dept_code = 'BME'
            elif 'AIDS' in raw_dept or 'AI&DS' in raw_dept: dept_code = 'AI&DS'
            
            # Fallback
            if dept_code not in dept_codes:
                for dc in dept_codes:
                    if dc in raw_dept:
                        dept_code = dc
                        break
            
            # 1. Ensure master data exists
            deg_obj = Degree.query.first()
            if not deg_obj:
                deg_obj = Degree(name='B.E')
                db.session.add(deg_obj); db.session.commit()

            d_obj = Department.query.filter_by(code=dept_code).first()
            if not d_obj:
                d_obj = Department(code=dept_code, name=dept_code, degree_id=deg_obj.id)
                db.session.add(d_obj); db.session.commit()
                dept_codes.append(dept_code)

            b_obj = Batch.query.filter_by(label=batch_label).first()
            if not b_obj:
                b_obj = Batch(label=batch_label)
                db.session.add(b_obj); db.session.commit()

            r_obj = Regulation.query.filter_by(name=reg_name).first()
            if not r_obj:
                r_obj = Regulation(name=reg_name)
                db.session.add(r_obj); db.session.commit()

            # 2. Get Curriculum
            curr = Curriculum.query.filter_by(department_id=d_obj.id, batch_id=b_obj.id, regulation_id=r_obj.id).first()
            if not curr:
                curr = Curriculum(department_id=d_obj.id, batch_id=b_obj.id, regulation_id=r_obj.id)
                db.session.add(curr); db.session.commit()

            is_lab = 'LAB' in title.upper() or 'PRACTICAL' in title.upper() or 'WORKSHOP' in title.upper()

            # 3. Check if Course exists in this curriculum
            existing = Course.query.filter_by(
                course_code=code,
                curriculum_id=curr.id
            ).first()

            if existing:
                existing.course_title = title
                existing.credits = credits
                existing.semester = sem
                existing.is_lab = is_lab
                updated += 1
            else:
                new_course = Course(
                    course_code=code,
                    course_title=title,
                    curriculum_id=curr.id,
                    credits=credits,
                    semester=sem,
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
