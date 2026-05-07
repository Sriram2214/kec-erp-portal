import pandas as pd
import os
import logging
from app import create_app, db
from app.models import Course, Curriculum, Degree, Department, Batch, Regulation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_curriculum(file_path):
    app = create_app()
    with app.app_context():
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return

        logger.info(f"Reading Excel file: {file_path}")
        df = pd.read_excel(file_path)
        df.columns = [c.strip() for c in df.columns]

        # Pre-fetch master data
        degrees = {d.name: d.id for d in Degree.query.all()}
        depts = {d.code: d.id for d in Department.query.all()}
        # For depts, we also need to map long names
        dept_names = {d.name.upper(): d.id for d in Department.query.all()}
        
        batches = {b.label: b.id for b in Batch.query.all()}
        regs = {r.name: r.id for r in Regulation.query.all()}

        added_curriculums = 0
        added_courses = 0
        
        # Helper to get/create Curriculum
        curriculum_cache = {}

        for _, row in df.iterrows():
            raw_batch = str(row['BATCH']).strip().replace(' ', '') # 2021-2025
            raw_reg = str(row['REGULATION']).strip()
            if not raw_reg.startswith('R'): raw_reg = f"R{raw_reg}"
            
            raw_dept = str(row['DEPARTMENT']).strip().upper()
            
            # Map Dept
            dept_id = None
            if 'COMPUTER SCIENCE AND ENGINEERING' in raw_dept and 'ARTIFICIAL' not in raw_dept: dept_id = depts.get('CSE')
            elif 'ELECTRONICS AND COMMUNICATION' in raw_dept: dept_id = depts.get('ECE')
            elif 'INFORMATION TECHNOLOGY' in raw_dept: dept_id = depts.get('IT')
            elif 'MECHANICAL' in raw_dept: dept_id = depts.get('MECH')
            elif 'DATA SCIENCE' in raw_dept: dept_id = depts.get('AI&DS')
            elif 'MACHINE LEARNING' in raw_dept: dept_id = depts.get('AIML')
            elif 'BIOMEDICAL' in raw_dept: dept_id = depts.get('BME')
            elif 'ROBOTICS' in raw_dept: dept_id = depts.get('RAA')
            else:
                # Try direct code match
                for code in depts:
                    if code in raw_dept:
                        dept_id = depts[code]
                        break
            
            if not dept_id:
                logger.warning(f"Could not map department: {raw_dept}")
                continue

            # Map Batch
            batch_id = batches.get(raw_batch)
            if not batch_id:
                # Create missing batch
                new_batch = Batch(label=raw_batch)
                db.session.add(new_batch)
                db.session.flush()
                batch_id = new_batch.id
                batches[raw_batch] = batch_id
                logger.info(f"Created missing batch: {raw_batch}")

            # Map Regulation
            reg_id = regs.get(raw_reg)
            if not reg_id:
                # Create missing regulation
                new_reg = Regulation(name=raw_reg)
                db.session.add(new_reg)
                db.session.flush()
                reg_id = new_reg.id
                regs[raw_reg] = reg_id
                logger.info(f"Created missing regulation: {raw_reg}")

            # Degree (Assume BE for all unless IT/AIDS/AIML)
            dept_code = [k for k, v in depts.items() if v == dept_id][0]
            degree_name = 'B.Tech' if dept_code in ['IT', 'AI&DS', 'AIML'] else 'BE'
            degree_id = degrees.get(degree_name)

            # 1. Get or Create Curriculum
            curr_key = (degree_id, dept_id, batch_id, reg_id)
            if curr_key not in curriculum_cache:
                curr = Curriculum.query.filter_by(
                    degree_id=degree_id, department_id=dept_id,
                    batch_id=batch_id, regulation_id=reg_id
                ).first()
                if not curr:
                    curr = Curriculum(
                        degree_id=degree_id, department_id=dept_id,
                        batch_id=batch_id, regulation_id=reg_id
                    )
                    db.session.add(curr)
                    db.session.flush()
                    added_curriculums += 1
                curriculum_cache[curr_key] = curr.id
            
            curr_id = curriculum_cache[curr_key]

            # 2. Add Course
            code = str(row['COURSE CODE']).strip()
            title = str(row['COURSE NAME']).strip()
            sem = int(row['SEM'])
            credits = int(row['CREDITS'])
            is_lab = any(x in title.upper() for x in ['LAB', 'PRACTICAL', 'WORKSHOP'])

            # Avoid duplicates within same curriculum
            existing_course = Course.query.filter_by(curriculum_id=curr_id, course_code=code).first()
            if not existing_course:
                course = Course(
                    curriculum_id=curr_id,
                    course_code=code,
                    course_title=title,
                    semester=sem,
                    credits=credits,
                    is_lab=is_lab
                )
                db.session.add(course)
                added_courses += 1

            if (added_courses) % 100 == 0:
                db.session.commit()
                logger.info(f"Processed {added_courses} courses...")

        db.session.commit()
        logger.info(f"Done! Created {added_curriculums} curriculums and {added_courses} courses.")

if __name__ == "__main__":
    seed_curriculum("COURSE DETAIL - 2021 TO 2025.xlsx")
