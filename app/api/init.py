from flask import Blueprint, jsonify
from app import db
from app.models import User, Degree, Department, Regulation, AcademicYear, Batch

init_bp = Blueprint('init_db', __name__)

@init_bp.route('/api/init-db')
def init_db():
    try:
        db.create_all()
        
        # Create Admin if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
        coe = User.query.filter_by(username='coe').first()
        if not coe:
            coe = User(username='coe', role='coe')
            coe.set_password('coe123')
            db.session.add(coe)
 
        # 1. Degrees
        if not Degree.query.first():
            for deg_name in ['B.E', 'B.TECH', 'M.E', 'PhD.']:
                db.session.add(Degree(name=deg_name))
            db.session.flush()

        # 2. Departments
        if not Department.query.first():
            be = Degree.query.filter_by(name='B.E').first()
            depts = [
                ('AI&DS', 'Artificial Intelligence and Data Science'),
                ('AIML', 'Artificial Intelligence and Machine Learning'),
                ('BME', 'Biomedical Engineering'),
                ('CSE', 'Computer Science and Engineering'),
                ('ECE', 'Electronics and Communication Engineering'),
                ('IT', 'Information Technology'),
                ('MECH', 'Mechanical Engineering'),
                ('RAA', 'Robotics and Automation')
            ]
            for code, name in depts:
                db.session.add(Department(code=code, name=name, degree_id=be.id if be else 1))

        if not Regulation.query.first():
            db.session.add(Regulation(name='R2021'))
            db.session.add(Regulation(name='R2019'))

        if not AcademicYear.query.first():
            ay = AcademicYear(label='2023-24', semester='ODD', is_current=True)
            db.session.add(ay)

        # 3. Batches
        if not Batch.query.first():
            for b in ['2021-2025', '2022-2026', '2023-2027', '2024-2028']:
                db.session.add(Batch(label=b))

        # 4. Demo Data (Courses & 500 Students)
        from app.models import Student, Course
        import random
        
        if not Course.query.first():
            courses = [
                ('CS8651', 'Internet Programming', 'CSE', 6),
                ('CS8691', 'Artificial Intelligence', 'CSE', 6),
                ('IT8601', 'Computational Intelligence', 'IT', 6),
                ('EC8691', 'Microprocessors and Microcontrollers', 'ECE', 6),
                ('EE8601', 'Solid State Drives', 'MECH', 6),
                ('GE2412', 'Universal Human Values', 'AI&DS', 6),
            ]
            for code, title, dept, sem in courses:
                db.session.add(Course(course_code=code, course_title=title, department=dept, semester=sem, credits=3))

        if Student.query.count() < 100:
            first_names = ["Aarav", "Vivaan", "Aditya", "Arjun", "Sai", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Karan", "Rohan", "Rahul", "Varun", "Vikram", "Sanjay", "Vijay", "Deepak", "Prakash", "Suresh", "Ramesh", "Karthik", "Gautam", "Harish", "Ashwin", "Manoj", "Prasad", "Aanya", "Diya", "Isha", "Kavya", "Meera", "Neha", "Priya", "Riya", "Sanya", "Tara", "Anjali", "Divya", "Pooja", "Sneha", "Swati"]
            last_names = ["Kumar", "Sharma", "Singh", "Patel", "Reddy", "Rao", "Iyer", "Pillai", "Nair", "Menon", "Jain", "Gupta", "Desai", "Joshi", "Bhatt", "Venkatesh", "Krishnan", "Rajan", "Natarajan", "Sundaram", "Murthy", "Balakrishnan", "Srinivasan", "Chandran", "Ramachandran", "Subramaniam", "Kannan", "Ganesan"]
            
            depts = ['AI&DS', 'AIML', 'BME', 'CSE', 'ECE', 'IT', 'MECH', 'RAA']
            dept_map = {'AI&DS':'AD', 'AIML':'AM', 'BME':'BM', 'CSE':'CS', 'ECE':'EC', 'IT':'IT', 'MECH':'ME', 'RAA':'RA'}
            
            for i in range(1, 501):
                dept = random.choice(depts)
                dept_code = '21' + dept_map[dept]
                reg_no = f"{dept_code}{str(i).zfill(3)}"
                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                
                db.session.add(Student(
                    register_number=reg_no,
                    name=name,
                    department=dept,
                    batch='2021-2025',
                    academic_year=3,
                    semester=6,
                    degree='B.E',
                    regulation='R2021',
                    email=f"stu{i}@kec.ac.in",
                    phone=f"98{str(random.randint(10000000, 99999999))}"
                ))

        db.session.commit()
        return jsonify({
            'message': 'Database initialized with KEC specific master data!',
            'status': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
