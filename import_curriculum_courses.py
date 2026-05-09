import csv
from app import create_app, db
from app.models import Course, Curriculum, Department, Degree, Batch, Regulation, Student, CourseRegistration

def import_courses_and_register(csv_path):
    app = create_app()
    with app.app_context():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            reg_count = 0
            
            # Cache for efficiency
            curriculums = {} # (degree_name, dept_name, batch_label, reg_name) -> curriculum_id
            
            for row in reader:
                try:
                    batch_raw = row['BATCH'].replace(' ', '')
                    reg_name = 'R' + row['REGULATION'].strip()
                    dept_full = row['DEPARTMENT'].strip()
                    sem = int(row['SEM'])
                    code = row['COURSE CODE'].strip().upper()
                    name = row['COURSE NAME'].strip()
                    
                    # Credits might be float strings like '4.0'
                    credits_raw = row.get('CREDITS', '0') or '0'
                    credits = int(float(credits_raw))
                    
                    # Parse Degree and Dept
                    degree_name = "BE"
                    dept_name = dept_full
                    if dept_full.startswith('B.E.'):
                        degree_name = 'BE'
                        dept_name = dept_full.replace('B.E.', '').strip()
                    elif dept_full.startswith('B.Tech.'):
                        degree_name = 'B.Tech'
                        dept_name = dept_full.replace('B.Tech.', '').strip()
                    elif dept_full.startswith('M.E.'):
                        degree_name = 'ME'
                        dept_name = dept_full.replace('M.E.', '').strip()
                    
                    # Handle specific dept name variations if needed
                    # e.g. "Computer Science and Engineering (Artificial Intelligence and Machine Learning)"
                    # matches our DB dept names? Yes.
                    
                    key = (degree_name, dept_name, batch_raw, reg_name)
                    
                    if key not in curriculums:
                        curr = Curriculum.query.join(Degree).join(Department).join(Batch).join(Regulation).filter(
                            Degree.name == degree_name,
                            Department.name == dept_name,
                            Batch.label == batch_raw,
                            Regulation.name == reg_name
                        ).first()
                        
                        if curr:
                            print(f"FOUND Curriculum: {key}", flush=True)
                            curriculums[key] = (curr.id, curr.department.code)
                        else:
                            print(f"NOT FOUND Curriculum: {key}", flush=True)
                            continue
                    
                    curr_id, dept_code = curriculums[key]
                    print(f"Processing Course: {code} for {key}", flush=True)
                    
                    # Check/Create Course
                    course = Course.query.filter_by(course_code=code, curriculum_id=curr_id).first()
                    if not course:
                        course = Course(
                            course_code=code,
                            course_title=name,
                            curriculum_id=curr_id,
                            semester=sem,
                            credits=credits
                        )
                        db.session.add(course)
                        db.session.flush()
                        count += 1
                        print(f"Added Course: {code}", flush=True)
                    
                    # Auto-Register Students using Dept CODE
                    # OPTIMIZED: Fetch all students and existing registrations in bulk
                    students = Student.query.filter_by(department=dept_code, batch=batch_raw).all()
                    if students:
                        existing_reg_student_ids = set(
                            row[0] for row in db.session.query(CourseRegistration.student_id)
                            .filter(CourseRegistration.course_id == course.id).all()
                        )
                        
                        new_regs = 0
                        for s in students:
                            if s.id not in existing_reg_student_ids:
                                db.session.add(CourseRegistration(student_id=s.id, course_id=course.id))
                                reg_count += 1
                                new_regs += 1
                        
                        if new_regs > 0:
                            print(f"  -> Registered {new_regs} new students", flush=True)
                    
                    # Commit every 100 courses to avoid timeout
                    if count % 10 == 0:
                        db.session.commit()
                        print(f"Committed batch... Total Courses: {count}, Regs: {reg_count}", flush=True)
                        
                except Exception as e:
                    print(f"Error processing row {row.get('COURSE CODE')}: {e}", flush=True)
                    db.session.rollback()
                    continue
            
            db.session.commit()
            print(f"FINISHED: Imported {count} courses and created {reg_count} registrations.", flush=True)

if __name__ == "__main__":
    import_courses_and_register('course_details_2021_2025.csv')
