import os
from app import create_app, db
from app.models import (AcademicYear, Course, Student, ExamSchedule, 
                        DummySticker, Department, Batch, Regulation, Degree)
import datetime

def seed():
    app = create_app()
    with app.app_context():
        print("Seeding ESE Sample Data...")

        # 1. Academic Year
        ay = AcademicYear.query.filter_by(is_current=True).first()
        if not ay:
            ay = AcademicYear(label='2025-26', semester='EVEN', is_current=True)
            db.session.add(ay)
            db.session.flush()

        # 2. Master Data (minimal)
        dept = Department.query.first()
        if not dept:
            dept = Department(name='CSE', code='CSE')
            db.session.add(dept)
        
        batch = Batch.query.first()
        if not batch:
            batch = Batch(label='2022-2026')
            db.session.add(batch)

        reg = Regulation.query.first()
        if not reg:
            reg = Regulation(name='R2023')
            db.session.add(reg)

        deg = Degree.query.first()
        if not deg:
            deg = Degree(name='B.E.', code='BE')
            db.session.add(deg)
        
        db.session.flush()

        # 3. Course
        course_code = 'GE241203'
        course = Course.query.filter_by(course_code=course_code).first()
        if not course:
            course = Course(
                course_code=course_code,
                course_title='Engineering Physics',
                semester=2,
                department='CSE',
                credits=3,
                regulation='R2023'
            )
            db.session.add(course)
            db.session.flush()

        # 4. Exam Schedule
        today = datetime.date.today()
        sch = ExamSchedule.query.filter_by(course_id=course.id).first()
        if not sch:
            sch = ExamSchedule(
                course_id=course.id,
                exam_date=today,
                session='FN',
                academic_year_id=ay.id
            )
            db.session.add(sch)
            db.session.flush()

        # 5. Students (40 students to test pagination/30-limit)
        print(f"Adding 40 students for {course_code}...")
        for i in range(1, 41):
            reg_no = f'210825104{i:03d}'
            stu = Student.query.filter_by(register_number=reg_no).first()
            if not stu:
                stu = Student(
                    register_number=reg_no,
                    name=f'STUDENT {i}',
                    email=f'stu{i}@kec.ac.in',
                    department='CSE',
                    semester=2,
                    batch='2022-2026',
                    degree='BE',
                    academic_year=1
                )
                db.session.add(stu)
                db.session.flush()
            
            # Add Dummy Stickers for first 35 students
            if i <= 35:
                ds = DummySticker.query.filter_by(student_id=stu.id, exam_schedule_id=sch.id).first()
                if not ds:
                    ds = DummySticker(
                        student_id=stu.id,
                        exam_schedule_id=sch.id,
                        dummy_number=f'DMY{700000 + i}',
                        foil_number=f'F{1000 + i}'
                    )
                    db.session.add(ds)

        db.session.commit()
        print("Seeding Complete!")
        print(f"   Course: {course_code}")
        print(f"   Exam Date: {today}")
        print(f"   Total Students: 40")
        print(f"   Dummy Numbers Uploaded: 35")

if __name__ == '__main__':
    seed()
