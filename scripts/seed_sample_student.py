import os
from app import create_app, db
from app.models import (AcademicYear, Course, Student, ExamSchedule, 
                        DummySticker, FoilMark)
import datetime

def seed():
    app = create_app()
    with app.app_context():
        print("Seeding Realistic Sample Student...")

        # 1. Academic Year
        ay = AcademicYear.query.filter_by(is_current=True).first()
        if not ay:
            ay = AcademicYear(label='2024-25', semester='ODD', is_current=True)
            db.session.add(ay)
            db.session.flush()

        # 2. Student: SURYA PRAKASH S
        regno = '210822205098'
        stu = Student.query.filter_by(register_number=regno).first()
        if not stu:
            stu = Student(
                register_number=regno,
                name='SURYA PRAKASH S',
                department='CSE',
                semester=5,
                batch='2022-2026',
                degree='B.E.',
                regulation='2021',
                dob='09/08/2004',
                phone='9876543210',
                academic_year=3
            )
            db.session.add(stu)
        else:
            stu.phone = '9876543210'
            stu.dob = '09/08/2004'
        db.session.flush()

        # 3. Courses & Exam Schedule (from the image)
        courses_data = [
            ('CCS341', 'Data Warehousing', 'A'),
            ('CCS355', 'Neural Networks and Deep Learning', 'A'),
            ('CS3551', 'Distributed Computing', 'B+'),
            ('CS3591', 'Computer Networks', 'B+'),
            ('CS3691', 'Embedded Systems and IoT', 'A'),
            ('GE3251', 'Engineering Graphics', 'U'),
            ('IT3501', 'Full Stack Web Development', 'A'),
            ('IT3511', 'Full Stack Web Development Laboratory', 'O'),
            ('MA3354', 'Discrete Mathematics', 'B'),
            ('NM1055', 'CCNA 1 Network Engineering', 'A+')
        ]

        print(f"Adding {len(courses_data)} courses and schedules...")
        today = datetime.date.today()
        for i, (code, title, grade) in enumerate(courses_data):
            # Course
            c = Course.query.filter_by(course_code=code).first()
            if not c:
                c = Course(
                    course_code=code,
                    course_title=title,
                    department='CSE',
                    semester=5 if 'GE' not in code else 2,
                    credits=3,
                    regulation='2021'
                )
                db.session.add(c)
                db.session.flush()
            
            # Schedule (spread dates)
            exam_date = today + datetime.timedelta(days=i*2)
            sch = ExamSchedule.query.filter_by(course_id=c.id, academic_year_id=ay.id).first()
            if not sch:
                sch = ExamSchedule(
                    course_id=c.id,
                    exam_date=exam_date,
                    session='FN' if i % 2 == 0 else 'AN',
                    academic_year_id=ay.id
                )
                db.session.add(sch)
                db.session.flush()
            
            # Dummy & Foil for Results
            dummy = f'DMY{800000 + i}'
            foil = f'F{5000 + i}'
            
            ds = DummySticker.query.filter_by(student_id=stu.id, exam_schedule_id=sch.id).first()
            if not ds:
                ds = DummySticker(student_id=stu.id, exam_schedule_id=sch.id, 
                                 dummy_number=dummy, foil_number=foil)
                db.session.add(ds)
                db.session.flush()
            
            fm = FoilMark.query.filter_by(dummy_number=dummy, course_id=c.id).first()
            if not fm:
                fm = FoilMark(dummy_number=dummy, foil_number=foil, course_id=c.id, grade=grade)
                db.session.add(fm)

        db.session.commit()
        print("Sample data for SURYA PRAKASH S seeded successfully!")

if __name__ == '__main__':
    seed()
