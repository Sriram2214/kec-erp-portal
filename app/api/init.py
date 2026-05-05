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

        db.session.commit()
        return jsonify({
            'message': 'Database initialized with KEC specific master data!',
            'status': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
