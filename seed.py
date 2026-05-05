from app import create_app, db
from app.models import User, Student, Faculty, AcademicYear, Degree, Department, Batch, Course, GradeScale
from werkzeug.security import generate_password_hash

def seed():
    app = create_app()
    
    with app.app_context():
        print("Cleaning up database...")
        db.drop_all()
        db.create_all()
        
        # 1. Create System Users
        print("Creating users...")
        users = [
            {'u': 'admin',   'p': 'admin123',   'r': 'admin'},
            {'u': 'coe',     'p': 'coe123',     'r': 'coe'},
            {'u': 'faculty', 'p': 'faculty123', 'r': 'faculty'},
            {'u': 'student', 'p': 'student123', 'r': 'student'}
        ]
        
        for u in users:
            hashed_pw = generate_password_hash(u['p'])
            new_user = User(username=u['u'], password_hash=hashed_pw, role=u['r'])
            db.session.add(new_user)
            
        # 2. Create Master Data
        print("Creating master data...")
        deg  = Degree(name="B.E")
        db.session.add(deg)
        db.session.commit()
        
        dept = Department(name="Computer Science and Engineering", code="CSE", degree_id=deg.id)
        batch = Batch(label="2021-2025")
        db.session.add_all([dept, batch])
        db.session.commit()
        
        # 3. Create a Sample Student (for login testing)
        student_profile = Student(
            register_number="student", 
            name="Sample Student",
            department="CSE",
            batch="2021-2025",
            academic_year=3,
            semester=6,
            email="student@kings.edu"
        )
        db.session.add(student_profile)
        
        # 4. Create Sample Exam Schedule
        print("Creating exam schedules...")
        courses = Course.query.limit(3).all()
        for i, c in enumerate(courses):
            sched = ExamSchedule(
                course_id=c.id,
                exam_date=dt.date.today() + dt.timedelta(days=i+5),
                session='FN' if i % 2 == 0 else 'AN',
                hall_number=f'HALL-{100+i}',
                student_strength=60
            )
            db.session.add(sched)
        
        # 5. Create Grade Scale
        print("Creating grade scales...")
        grades = [
            ('O', 91, 100, 10), ('A+', 81, 90, 9), ('A', 71, 80, 8),
            ('B+', 61, 70, 7),  ('B', 56, 60, 6), ('C', 50, 55, 5), ('U', 0, 49, 0)
        ]
        for g, mi, ma, p in grades:
            db.session.add(GradeScale(grade=g, min_mark=mi, max_mark=ma, points=p))
            
        db.session.commit()
        print("[SUCCESS] Database seeded successfully with Grade Data!")
        print("--- CREDENTIALS ---")
        print("COE Login: coe / coe123")
        print("Admin: admin / admin123")
        print("Faculty: faculty / faculty123")
        print("Student: student / student123")

if __name__ == "__main__":
    seed()
