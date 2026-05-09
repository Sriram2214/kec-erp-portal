import csv
import os
import sys
from app import create_app, db
from app.models import (
    Curriculum, Course, Student, CourseRegistration,
    Degree, Department, Batch, Regulation
)
from sqlalchemy import text

# Mapping CSV "DEPARTMENT" column to DB Department Name and Degree Name
CSV_DEPT_MAP = {
    "B.E. Biomedical Engineering": ("Biomedical Engineering", "BE"),
    "B.E. Computer Science and Engineering": ("Computer Science and Engineering", "BE"),
    "B.E. Computer Science and Engineering (Artificial Intelligence and Machine Learning)": 
        ("Computer Science and Engineering (Artificial Intelligence and Machine Learning)", "BE"),
    "B.E. Electronics and Communication Engineering": ("Electronics and Communication Engineering", "BE"),
    "B.E. Mechanical Engineering": ("Mechanical Engineering", "BE"),
    "B.E. Robotics and Automation": ("Robotics and Automation", "BE"),
    "B.Tech. Artificial Intelligence and Data Science": ("Artificial Intelligence and Data Science", "B.Tech"),
    "B.Tech. Information Technology": ("Information Technology", "B.Tech"),
    "M.E. Computer Science and Engineering": ("Computer Science and Engineering", "ME"),
}

def rebuild_academic_data(csv_path="course_details_2021_2025.csv"):
    app = create_app()
    with app.app_context():
        print("="*60)
        print("KCE MASTER ACADEMIC REBUILD ENGINE")
        print(f"Source: {csv_path}")
        print("="*60)

        # --------------------------------------------------
        # PHASE 1: Cleanup (Mandatory Fix Plan)
        # --------------------------------------------------
        print("\nPHASE 1: Cleanup...")
        
        # 1. Delete invalid generic curriculums (Batch 2023-2027 | R2021)
        bad_currs = Curriculum.query.join(Batch).join(Regulation).filter(
            Batch.label == '2023-2027',
            Regulation.name == 'R2021'
        ).all()
        
        if bad_currs:
            for curr in bad_currs:
                CourseRegistration.query.join(Course).filter(Course.curriculum_id == curr.id).delete(synchronize_session=False)
                Course.query.filter_by(curriculum_id=curr.id).delete(synchronize_session=False)
                db.session.delete(curr)
            print(f"  -> Deleted {len(bad_currs)} invalid generic curriculums.")
        
        # 2. Clear corrupted registrations (Mismatching Dept/Batch/Reg)
        # This is critical for data integrity
        all_regs = CourseRegistration.query.all()
        deleted_reg_count = 0
        for reg in all_regs:
            s = reg.student
            c = reg.course
            if not c or not c.curriculum: continue
            cur = c.curriculum
            
            if (s.department != cur.department.code or 
                s.batch != cur.batch.label or 
                s.regulation != cur.regulation.name):
                db.session.delete(reg)
                deleted_reg_count += 1
        
        if deleted_reg_count > 0:
            print(f"  -> Deleted {deleted_reg_count} corrupted registrations.")
            
        db.session.commit()

        # --------------------------------------------------
        # PHASE 2: Load Master Data Caches
        # --------------------------------------------------
        print("\nPHASE 2: Loading Master Data...")
        curricula = Curriculum.query.all()
        curr_map = {(c.degree.name, c.department.name, c.batch.label, c.regulation.name): c for c in curricula}
            
        students = Student.query.all()
        student_groups = {}
        for s in students:
            key = (s.department, s.batch, s.regulation)
            if key not in student_groups:
                student_groups[key] = []
            student_groups[key].append(s)
        print(f"  -> Loaded {len(curr_map)} curricula and {len(students)} students.")

        # --------------------------------------------------
        # PHASE 3: Process CSV
        # --------------------------------------------------
        print(f"\nPHASE 3: Processing {csv_path}...")
        
        if not os.path.exists(csv_path):
            print(f"ERROR: {csv_path} not found!")
            return

        courses_created = 0
        registrations_created = 0
        row_count = 0
        
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1
                csv_dept = row['DEPARTMENT'].strip()
                batch_label = row['BATCH'].strip().replace(" ", "")
                reg_name = "R" + row['REGULATION'].strip() if not row['REGULATION'].strip().startswith('R') else row['REGULATION'].strip()
                
                if csv_dept not in CSV_DEPT_MAP:
                    continue
                
                dept_name, deg_name = CSV_DEPT_MAP[csv_dept]
                curr_key = (deg_name, dept_name, batch_label, reg_name)
                curriculum = curr_map.get(curr_key)
                
                if not curriculum:
                    continue

                # Course Check/Create
                course_code = row['COURSE CODE'].strip().upper()
                course = Course.query.filter_by(course_code=course_code, curriculum_id=curriculum.id).first()
                if not course:
                    course = Course(
                        course_code=course_code,
                        course_title=row['COURSE NAME'].strip(),
                        credits=float(row['CREDITS']) if row['CREDITS'] else 0.0,
                        semester=int(row['SEM']),
                        curriculum_id=curriculum.id
                    )
                    db.session.add(course)
                    db.session.flush()
                    courses_created += 1

                # Registration (Optimized)
                group_key = (curriculum.department.code, curriculum.batch.label, curriculum.regulation.name)
                eligible_students = student_groups.get(group_key, [])
                
                if eligible_students:
                    existing_reg_ids = set(r[0] for r in db.session.query(CourseRegistration.student_id).filter_by(course_id=course.id).all())
                    for s in eligible_students:
                        if s.id not in existing_reg_ids:
                            db.session.add(CourseRegistration(student_id=s.id, course_id=course.id))
                            registrations_created += 1

                if row_count % 100 == 0:
                    db.session.commit()
                    print(f"  Processed {row_count} rows...")

        db.session.commit()
        print(f"\nFINISHED: Created {courses_created} courses and {registrations_created} registrations.")

        # --------------------------------------------------
        # PHASE 4: Final Validation
        # --------------------------------------------------
        print("\nPHASE 4: Final Integrity Validation...")
        validation_query = text("""
            SELECT COUNT(*)
            FROM course_registration cr
            JOIN student s ON s.id = cr.student_id
            JOIN course c ON c.id = cr.course_id
            JOIN curriculum cur ON cur.id = c.curriculum_id
            JOIN department d ON d.id = cur.department_id
            JOIN batch b ON b.id = cur.batch_id
            JOIN regulation r ON r.id = cur.regulation_id
            WHERE s.department != d.code OR s.batch != b.label OR s.regulation != r.name;
        """)
        try:
            mismatches = db.session.execute(validation_query).scalar()
            if mismatches == 0:
                print("SUCCESS: 0 Mismatches found. Data is 100% clean.")
            else:
                print(f"WARNING: {mismatches} mismatches still exist in registrations!")
        except Exception as e:
            print(f"Validation Error: {e}")

if __name__ == "__main__":
    # Use the specified CSV as source of truth
    rebuild_academic_data("course_details_2021_2025.csv")
