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
        for code, title, dept, sem in courses_to_ensure:
            exists = Course.query.filter_by(course_code=code).first()
            if not exists:
                db.session.add(Course(course_code=code, course_title=title, department=dept, semester=sem, credits=3))
        db.session.commit()

        courses = Course.query.all()
        if not courses:
            print('No courses found!')
            return

        # ── 1. Cascading Cleanup (Correct Order) ──
        print('Cleaning existing records (Attendance, Dummies, Schedules, Registrations)...')
        from app.models import Attendance, DummySticker
        Attendance.query.delete()
        DummySticker.query.delete()
        CourseRegistration.query.delete()
        ExamSchedule.query.delete()
        db.session.commit()

        total_reg = 0
        total_sch = 0

        for course in courses:
            print(f'Processing {course.course_code} - {course.course_title} (Dept: {course.department}, Sem: {course.semester})')
            
            # Find students matching the course criteria
            students = Student.query.filter_by(
                department=course.department,
                semester=course.semester
            ).all()

            if not students:
                print(f'  ! No students found for {course.department} Sem {course.semester}. Skipping registration.')
            else:
                # Register all matching students for this course
                registrations = []
                for s in students:
                    registrations.append(CourseRegistration(
                        student_id=s.id,
                        course_id=course.id,
                        academic_year_id=ay.id
                    ))
                db.session.bulk_save_objects(registrations)
                total_reg += len(registrations)
                print(f'  [OK] Registered {len(registrations)} students.')

            # Create an exam schedule for this course
            # Random date in the next 15 days
            exam_date = datetime.date.today() + datetime.timedelta(days=random.randint(1, 15))
            session = random.choice(['FN', 'AN'])
            
            schedule = ExamSchedule(
                course_id=course.id,
                academic_year_id=ay.id,
                exam_date=exam_date,
                session=session,
                venue='MAIN BLOCK'
            )
            db.session.add(schedule)
            total_sch += 1

        db.session.commit()
        print('\n' + '='*40)
        print(f'SUCCESS!')
        print(f'Total Registrations: {total_reg}')
        print(f'Total Exam Schedules: {total_sch}')
        print('='*40)

if __name__ == '__main__':
    seed_exam_data()
