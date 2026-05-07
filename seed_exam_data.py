import random
import datetime
from app import create_app, db
from app.models import Student, Course, CourseRegistration, ExamSchedule, AcademicYear

app = create_app()

def seed_exam_data():
    with app.app_context():
        print('Starting exam data seeding...')
        
        ay = AcademicYear.query.filter_by(is_current=True).first()
        if not ay:
            print('Creating Academic Year...')
            ay = AcademicYear(label='2023-24', semester='EVEN', is_current=True)
            db.session.add(ay)
            db.session.commit()

        courses_to_ensure = [
            ('CS8651', 'Internet Programming', 'CSE', 6),
            ('CS8691', 'Artificial Intelligence', 'CSE', 6),
            ('CS8075', 'Data Warehousing and Data Mining', 'CSE', 7),
            ('CS8081', 'Internet of Things', 'CSE', 8),
            ('IT8601', 'Computational Intelligence', 'IT', 6),
            ('IT8076', 'Software Testing', 'IT', 7),
            ('IT8761', 'Security Laboratory', 'IT', 8),
            ('EC8691', 'Microprocessors and Microcontrollers', 'ECE', 6),
            ('EC8094', 'Satellite Communication', 'ECE', 7),
            ('EC8092', 'Advanced Wireless Communication', 'ECE', 8),
            ('EE8601', 'Solid State Drives', 'MECH', 6),
            ('ME8091', 'Automobile Engineering', 'MECH', 7),
            ('ME8073', 'Unconventional Machining Processes', 'MECH', 8),
            ('GE2412', 'Universal Human Values', 'AI&DS', 6),
            ('AD8501', 'Optimization Techniques', 'AI&DS', 5),
            ('AD8012', 'Software Project Management', 'AI&DS', 7),
            ('RA3601', 'Autonomous Systems', 'RAA', 6),
            ('RA3401', 'Robot Kinematics', 'RAA', 4),
        ]
        from app.models import Curriculum, Department, Batch, Regulation
        
        for code, title, dept_code, sem in courses_to_ensure:
            exists = Course.query.filter_by(course_code=code).first()
            if not exists:
                d = Department.query.filter_by(code=dept_code).first()
                if not d: continue
                b = Batch.query.first() # Assume first batch
                r = Regulation.query.first()
                curr = Curriculum.query.filter_by(department_id=d.id, batch_id=b.id, regulation_id=r.id).first()
                if not curr:
                    curr = Curriculum()
                    curr.department_id = d.id
                    curr.batch_id = b.id
                    curr.regulation_id = r.id
                    curr.degree_id = d.degree_id
                    db.session.add(curr); db.session.flush()
                
                c = Course()
                c.course_code = code
                c.course_title = title
                c.curriculum_id = curr.id
                c.semester = sem
                c.credits = 3
                db.session.add(c)
        db.session.commit()

        courses = Course.query.all()
        if not courses:
            print('No courses found!')
            return

        # ── 1. Cascading Cleanup ──
        from app.models import Attendance, DummySticker
        Attendance.query.delete()
        DummySticker.query.delete()
        CourseRegistration.query.delete()
        ExamSchedule.query.delete()
        db.session.commit()

        total_reg = 0
        total_sch = 0

        for course in courses:
            dept_obj = course.curriculum.department
            print(f'Processing {course.course_code} (Dept: {dept_obj.code}, Sem: {course.semester})')
            
            students = Student.query.filter_by(
                department=dept_obj.code,
                semester=course.semester
            ).all()

            if students:
                for s in students:
                    cr = CourseRegistration()
                    cr.student_id = s.id
                    cr.course_id = course.id
                    cr.academic_year_id = ay.id
                    db.session.add(cr)
                total_reg += len(students)

            exam_date = datetime.date.today() + datetime.timedelta(days=random.randint(1, 15))
            session = random.choice(['FN', 'AN'])
            
            sch = ExamSchedule()
            sch.course_id = course.id
            sch.academic_year_id = ay.id
            sch.exam_date = exam_date
            sch.session = session
            sch.venue = 'MAIN BLOCK'
            db.session.add(sch)
            total_sch += 1

        db.session.commit()
        print('\n' + '='*40)
        print(f'SUCCESS!')
        print(f'Total Registrations: {total_reg}')
        print(f'Total Exam Schedules: {total_sch}')
        print('='*40)

if __name__ == '__main__':
    seed_exam_data()
