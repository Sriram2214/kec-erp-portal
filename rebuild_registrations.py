import datetime
from app import create_app, db
from app.models import Student, CourseRegistration, Course, Curriculum, Department, Regulation, Batch

def rebuild():
    app = create_app()
    with app.app_context():
        print("--- Rebuilding Course Registrations ---")
        all_students = Student.query.all()
        
        # Pre-fetch master data
        depts = {d.code: d.id for d in Department.query.all()}
        batches = {b.label: b.id for b in Batch.query.all()}
        regs = {r.name: r.id for r in Regulation.query.all()}
        curriculums = {(c.department_id, c.batch_id, c.regulation_id): c.id for c in Curriculum.query.all()}
        
        course_map = {}
        for c in Course.query.all():
            key = (c.curriculum_id, c.semester)
            if key not in course_map: course_map[key] = []
            course_map[key].append(c.id)
            
        print(f"Processing {len(all_students)} students...")
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
                        # Register for all courses in their current semester
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
                    print(f"  Processed {i+1} students... Total Regs: {total_regs}", end='\r')

            if registrations_to_add:
                db.session.bulk_insert_mappings(CourseRegistration, registrations_to_add)
                db.session.commit()
                
        print(f"\nRebuild complete! Total registrations: {total_regs}")

if __name__ == "__main__":
    rebuild()
