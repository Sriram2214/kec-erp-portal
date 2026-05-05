
from flask import Blueprint, jsonify
from app import db
from app.models import User, Degree, Department, Regulation, AcademicYear, Batch

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

        # Basic Master Data
        if not Degree.query.first():
            be = Degree(name='BE')
            db.session.add(be)
            db.session.flush()
            
            depts = [
                ('CSE', 'Computer Science and Engineering'),
                ('ECE', 'Electronics and Communication Engineering'),
                ('EEE', 'Electrical and Electronics Engineering'),
                ('MECH', 'Mechanical Engineering'),
                ('IT', 'Information Technology'),
                ('AI&ML', 'Artificial Intelligence and Machine Learning'),
                ('BME', 'Biomedical Engineering'),
                ('RA', 'Robotics and Automation')
            ]
            for code, name in depts:
                db.session.add(Department(code=code, name=name, degree_id=be.id))

        if not Regulation.query.first():
            db.session.add(Regulation(name='R2021'))
            db.session.add(Regulation(name='R2019'))

        if not AcademicYear.query.first():
            ay = AcademicYear(label='2023-24', semester='ODD', is_current=True)
            db.session.add(ay)

        if not Batch.query.first():
            db.session.add(Batch(label='2021-2025'))
            db.session.add(Batch(label='2022-2026'))
            db.session.add(Batch(label='2023-2027'))

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
