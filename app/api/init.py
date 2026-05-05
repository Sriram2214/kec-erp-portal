
from flask import Blueprint, jsonify
from app import db
from app.models import User, Degree, Department, Regulation, AcademicYear, Batch, Student
import random

init_bp = Blueprint('init', __name__)

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
            
        # Create COE if not exists
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
            # Associate depts with B.E by default for now
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

        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "Database initialized with admin/coe accounts and master data.",
            "accounts": {
                "admin": "admin / admin123",
                "coe": "coe / coe123"
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
@init_bp.route('/api/seed-students')
def seed_students():
    try:
        # Check if already seeded
        if Student.query.count() > 100:
            return jsonify({"status": "info", "message": "Students already seeded."})

        depts = Department.query.all()
        if not depts:
            return jsonify({"status": "error", "message": "Please run /api/init-db first to create departments."}), 400
            
        batch = Batch.query.first()
        ay = AcademicYear.query.filter_by(is_current=True).first()
        
        first_names = ["Abishek", "Akash", "Anand", "Aravind", "Ashwin", "Balaji", "Bharath", "Chandru", "Dhanush", "Dharani", "Dinesh", "Ganesh", "Gokul", "Hari", "Harish", "Jagan", "Jayasurya", "Karthick", "Kishore", "Logesh", "Manikandan", "Mohan", "Mukesh", "Naveen", "Nithish", "Prabhu", "Prakash", "Pranav", "Praveen", "Ragul", "Rajesh", "Ranjith", "Sakthi", "Sandeep", "Sanjay", "Saravanan", "Sathish", "Selvakumar", "Siva", "Sriram", "Suresh", "Surya", "Tamil", "Tharun", "Thirumoorthy", "Venkatesan", "Vijay", "Vikram", "Vinoth", "Vishnu"]
        last_names = ["M", "R", "S", "B", "K", "V", "P", "A", "G", "J"]
        
        students = []
        for i in range(1, 2001):
            dept = random.choice(depts)
            reg_no = f"911221104{str(i).zfill(3)}"
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            s = Student(
                register_number=reg_no,
                name=name,
                department=dept.code,
                batch=batch.label if batch else "2021-2025",
                academic_year=ay.id if ay else 1,
                semester=1,
                degree="BE",
                regulation="R2021"
            )
            students.append(s)
            
            # Batch commit every 500 to prevent timeout/memory issues
            if len(students) >= 500:
                db.session.bulk_save_objects(students)
                db.session.commit()
                students = []
                
        if students:
            db.session.bulk_save_objects(students)
            db.session.commit()
            
        return jsonify({"status": "success", "message": "2000 students seeded successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
