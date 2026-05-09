import pandas as pd
from app import create_app, db
from app.models import Student, CourseRegistration, Attendance, DummySticker, FoilMark, Course, Curriculum, Department, Regulation, Batch
from sqlalchemy import text
import datetime
import time

def migrate():
    app = create_app()
    with app.app_context():
        print("--- STEP 1: Deleting Transactional Data (TRUNCATE) ---")
        # TRUNCATE is much faster and bypasses row-level locking/timeout issues in most cases
        tables_to_clear = ['foil_mark', 'dummy_sticker', 'attendance', 'course_registration', 'student']
        
        try:
            # Joining all tables in one truncate command is more efficient
            tables_str = ", ".join(tables_to_clear)
            db.session.execute(text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE"))
            db.session.commit()
            print(f"Tables {tables_str} truncated successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Truncate failed, falling back to manual delete. Error: {e}")
            for table in tables_to_clear:
                db.session.execute(text(f"DELETE FROM {table}"))
            db.session.commit()
            print("Transactional data cleared via manual delete.")

        print("\n--- STEP 2: Importing Original Student Data ---")
        df = pd.read_csv('original_student_details.csv')
        df['REGISTER NO'] = df['REGISTER NO'].astype(str).str.strip().str.upper()
        df = df.drop_duplicates(subset=['REGISTER NO'])
        
        dept_map = {'AI&ML': 'AIML', 'M.E - CSE': 'CSE', 'PHD': 'CSE'}
        
        students_added = 0
        students_list = []
        for _, row in df.iterrows():
            reg_no = row['REGISTER NO']
            dept_code = str(row['DEPT']).strip()
            dept_code = dept_map.get(dept_code, dept_code)
            
            reg_val = str(row['REGULATION']).strip()
            reg_name = f"R{reg_val}" if not reg_val.startswith('R') else reg_val
            
            year_short = reg_no[4:6]
            if not year_short.isdigit(): year_short = reg_no[:2]
            
            batch_start = f"20{year_short}"
            degree_branch = str(row['DEGREE & BRANCH'])
            is_pg = 'M.E' in degree_branch or 'PHD' in degree_branch or 'M.E' in str(row['DEPT'])
            duration = 2 if is_pg else 4
            batch_label = f"{batch_start}-{int(batch_start)+duration}"
            
            academic_year_num = 2025 - int(batch_start)
            if academic_year_num < 1: academic_year_num = 1
            if academic_year_num > duration: academic_year_num = duration
            
            s = Student(
                register_number=reg_no,
                name=str(row['NAME OF THE STUDENT']).strip().upper(),
                department=dept_code,
                batch=batch_label,
                academic_year=academic_year_num,
                semester=academic_year_num * 2,
                degree='ME' if is_pg else 'BE',
                regulation=reg_name,
                dob=str(row['DOB']).strip()
            )
            students_list.append(s)
            students_added += 1
            
            if len(students_list) >= 500:
                db.session.bulk_save_objects(students_list)
                db.session.commit()
                students_list = []
                print(f"Imported {students_added} students...", end='\r')
            
        if students_list:
            db.session.bulk_save_objects(students_list)
            db.session.commit()
        print(f"\nImported total {students_added} students.")

        print("\n--- STEP 3: Rebuilding Course Registrations (Optimized) ---")
        # Refresh session to get new IDs
        db.session.expire_all()
        all_students = Student.query.all()
        
        print("Pre-fetching curriculum data...")
        depts = {d.code: d.id for d in Department.query.all()}
        batches = {b.label: b.id for b in Batch.query.all()}
        regs = {r.name: r.id for r in Regulation.query.all()}
        curriculums = {(c.department_id, c.batch_id, c.regulation_id): c.id for c in Curriculum.query.all()}
        
        course_map = {}
        for c in Course.query.all():
            key = (c.curriculum_id, c.semester)
            if key not in course_map: course_map[key] = []
            course_map[key].append(c.id)
            
        print("Rebuilding registrations in batches...")
        registrations_to_add = []
        batch_size = 1000
        total_regs = 0
        
        with db.session.no_autoflush:
            for i, s in enumerate(all_students):
                d_id = depts.get(s.department)
                b_id = batches.get(s.batch)
                r_id = regs.get(s.regulation)
                
                if d_id and b_id and r_id:
                    curr_id = curriculums.get((d_id, b_id, r_id))
                    if curr_id:
                        courses = course_map.get((curr_id, s.semester), [])
                        for c_id in courses:
                            registrations_to_add.append({
                                'student_id': s.id,
                                'course_id': c_id,
                                'registered_on': datetime.datetime.utcnow(),
                                'is_backlog': False
                            })
                            total_regs += 1
                
                if len(registrations_to_add) >= batch_size:
                    db.session.bulk_insert_mappings(CourseRegistration, registrations_to_add)
                    db.session.commit()
                    registrations_to_add = []
                    print(f"Processed {i+1} students... Total Regs: {total_regs}", end='\r')

            if registrations_to_add:
                db.session.bulk_insert_mappings(CourseRegistration, registrations_to_add)
                db.session.commit()
                
        print(f"\nRebuilt {total_regs} course registrations.")

        print("\n--- FINAL VALIDATION ---")
        student_count = Student.query.count()
        print(f"Total Students: {student_count}")
        duplicate_check = db.session.execute(text("SELECT register_number, COUNT(*) FROM student GROUP BY register_number HAVING COUNT(*) > 1")).fetchall()
        
        if student_count == 2553 and len(duplicate_check) == 0:
            print("\nMIGRATION SUCCESSFUL!")
        else:
            print(f"\nWARNING: Validation issues. Count: {student_count}, Duplicates: {len(duplicate_check)}")

if __name__ == "__main__":
    migrate()
