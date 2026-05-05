from datetime import date
from app import create_app, db
from app.models import User, Student, Faculty, Course, CourseAllocation, ExamSchedule

app = create_app()

with app.app_context():
    db.create_all()

    # ── Admin User ──────────────────────────────────
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("Created admin user: admin / admin123")

    if not User.query.filter_by(username='staff').first():
        staff = User(username='staff', role='staff')
        staff.set_password('staff123')
        db.session.add(staff)
        print("Created staff user: staff / staff123")

    # ── Courses ─────────────────────────────────────
    courses_data = [
        ('CS301', 'Data Structures and Algorithms', 'CSE', 4),
        ('CS302', 'Database Management Systems',   'CSE', 3),
        ('CS303', 'Computer Networks',              'CSE', 3),
        ('EC301', 'Digital Signal Processing',      'ECE', 4),
        ('ME301', 'Engineering Thermodynamics',     'MECH', 3),
    ]
    created_courses = {}
    for code, title, dept, credits in courses_data:
        if not Course.query.filter_by(course_code=code).first():
            c = Course(course_code=code, course_title=title, department=dept, credits=credits)
            db.session.add(c)
            db.session.flush()
            created_courses[code] = c
            print(f"Added course: {code}")
        else:
            created_courses[code] = Course.query.filter_by(course_code=code).first()

    db.session.commit()

    # ── Faculty ─────────────────────────────────────
    faculty_data = [
        ('FAC001', 'Dr. R. Ramesh',     'CSE'),
        ('FAC002', 'Dr. S. Priya',      'CSE'),
        ('FAC003', 'Dr. K. Murugan',    'ECE'),
        ('FAC004', 'Prof. T. Selvam',   'MECH'),
    ]
    created_faculty = {}
    for eid, name, dept in faculty_data:
        if not Faculty.query.filter_by(employee_id=eid).first():
            f = Faculty(employee_id=eid, name=name, department=dept)
            db.session.add(f)
            db.session.flush()
            created_faculty[eid] = f
            print(f"Added faculty: {eid} - {name}")
        else:
            created_faculty[eid] = Faculty.query.filter_by(employee_id=eid).first()

    db.session.commit()

    # ── Course Allocations ───────────────────────────
    alloc_data = [
        ('FAC001', 'CS301', '2022-2026'),
        ('FAC002', 'CS302', '2022-2026'),
        ('FAC002', 'CS303', '2022-2026'),
        ('FAC003', 'EC301', '2022-2026'),
        ('FAC004', 'ME301', '2022-2026'),
    ]
    for feid, ccode, batch in alloc_data:
        f = created_faculty.get(feid)
        c = created_courses.get(ccode)
        if f and c:
            exists = CourseAllocation.query.filter_by(faculty_id=f.id, course_id=c.id, batch=batch).first()
            if not exists:
                alloc = CourseAllocation(faculty_id=f.id, course_id=c.id, batch=batch)
                db.session.add(alloc)

    db.session.commit()

    # ── Exam Schedules ───────────────────────────────
    exam_data = [
        ('CS301', date(2026, 5, 10), 'FN'),
        ('CS302', date(2026, 5, 12), 'AN'),
        ('CS303', date(2026, 5, 14), 'FN'),
        ('EC301', date(2026, 5, 11), 'FN'),
        ('ME301', date(2026, 5, 13), 'AN'),
    ]
    for ccode, edate, session in exam_data:
        c = created_courses.get(ccode)
        if c and not ExamSchedule.query.filter_by(course_id=c.id, exam_date=edate, session=session).first():
            sched = ExamSchedule(course_id=c.id, exam_date=edate, session=session)
            db.session.add(sched)
            print(f"Added exam schedule: {ccode} on {edate} {session}")

    db.session.commit()

    # ── Students ─────────────────────────────────────
    if Student.query.count() == 0:
        students = [
            # CSE Batch
            Student(register_number='311022104001', name='Arjun Kumar S',    department='CSE', batch='2022-2026', academic_year=3),
            Student(register_number='311022104002', name='Priya Dharshini R', department='CSE', batch='2022-2026', academic_year=3),
            Student(register_number='311022104003', name='Karthik Rajan M',  department='CSE', batch='2022-2026', academic_year=3),
            Student(register_number='311022104004', name='Divya Lakshmi P',  department='CSE', batch='2022-2026', academic_year=3),
            Student(register_number='311022104005', name='Muruganantham T',  department='CSE', batch='2022-2026', academic_year=3),
            Student(register_number='311022104006', name='Nandhini G',       department='CSE', batch='2022-2026', academic_year=3),
            Student(register_number='311022104007', name='Suriya Prakash V', department='CSE', batch='2022-2026', academic_year=3),
            Student(register_number='311022104008', name='Sowmiya K',        department='CSE', batch='2022-2026', academic_year=3),
            # ECE Batch
            Student(register_number='311022107001', name='Aravind S',        department='ECE', batch='2022-2026', academic_year=3),
            Student(register_number='311022107002', name='Meena R',          department='ECE', batch='2022-2026', academic_year=3),
            Student(register_number='311022107003', name='Vignesh P',        department='ECE', batch='2022-2026', academic_year=3),
            # MECH Batch
            Student(register_number='311022101001', name='Rajesh Kumar D',   department='MECH', batch='2022-2026', academic_year=3),
            Student(register_number='311022101002', name='Senthil Kumar M',  department='MECH', batch='2022-2026', academic_year=3),
        ]
        db.session.bulk_save_objects(students)
        db.session.commit()
        print(f"Seeded {len(students)} students.")

    print("\n✅ Database seeded successfully!")
    print(f"   Students : {Student.query.count()}")
    print(f"   Courses  : {Course.query.count()}")
    print(f"   Faculty  : {Faculty.query.count()}")
    print(f"   Schedules: {ExamSchedule.query.count()}")
    print("\nLogin credentials:")
    print("  Admin → admin / admin123")
    print("  Staff → staff / staff123")
