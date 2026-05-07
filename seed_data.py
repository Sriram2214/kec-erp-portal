import datetime
from app import create_app, db
from app.models import Course, ExamSchedule, Student, Department, Batch, Regulation, Curriculum, Degree

def seed():
    app = create_app()
    with app.app_context():
        # Ensure Master Data
        deg = Degree.query.first()
        if not deg:
            deg = Degree()
            deg.name = 'B.E'
            db.session.add(deg); db.session.commit()
            
        d = Department.query.filter_by(code='CSE').first()
        if not d:
            d = Department()
            d.code = 'CSE'
            d.name = 'Computer Science and Engineering'
            d.degree_id = deg.id
            db.session.add(d); db.session.commit()
            
        b = Batch.query.filter_by(label='2021-2025').first()
        if not b:
            b = Batch()
            b.label = '2021-2025'
            db.session.add(b); db.session.commit()
            
        r = Regulation.query.filter_by(name='R2021').first()
        if not r:
            r = Regulation()
            r.name = 'R2021'
            db.session.add(r); db.session.commit()
            
        curr = Curriculum.query.filter_by(department_id=d.id, batch_id=b.id, regulation_id=r.id).first()
        if not curr:
            curr = Curriculum()
            curr.department_id = d.id
            curr.batch_id = b.id
            curr.regulation_id = r.id
            curr.degree_id = deg.id
            db.session.add(curr); db.session.commit()

        # 1. Add a course if not exists
        course = Course.query.filter_by(course_code='GE241203').first()
        if not course:
            course = Course()
            course.course_code = 'GE241203'
            course.course_title = 'ENGINEERING PHYSICS'
            course.curriculum_id = curr.id
            course.credits = 4
            course.semester = 1
            db.session.add(course)
            db.session.commit()
        else:
            course.course_title = 'ENGINEERING PHYSICS'
            course.semester = 1
            db.session.commit()

        # 2. Add an exam schedule if not exists
        today = datetime.date.today()
        schedule = ExamSchedule.query.filter_by(course_id=course.id, exam_date=today).first()
        if not schedule:
            schedule = ExamSchedule()
            schedule.course_id = course.id
            schedule.exam_date = today
            schedule.session = 'FN'
            schedule.venue = 'MAIN-HALL-1'
            db.session.add(schedule)
            db.session.commit()

        # 3. Add some students for this semester if not exists
        if Student.query.filter_by(semester=1).count() == 0:
            students = [
                ('911221104001', 'ABISHEK M', 'CSE', '2021-2025', 1),
                ('911221104002', 'AKASH R', 'CSE', '2021-2025', 1),
                ('911221104003', 'BALAJI S', 'CSE', '2021-2025', 1),
                ('911221104004', 'CHANDRU K', 'CSE', '2021-2025', 1),
                ('911221104005', 'DHARANI P', 'CSE', '2021-2025', 1)
            ]
            for reg, name, dept, bt, sem in students:
                s = Student()
                s.register_number = reg
                s.name = name
                s.department = dept
                s.batch = bt
                s.academic_year = 1
                s.semester = sem
                db.session.add(s)
            db.session.commit()

        print("Data seeded successfully using SQLAlchemy.")

if __name__ == '__main__':
    seed()
