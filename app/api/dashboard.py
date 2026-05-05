from flask import jsonify
from flask_login import login_required, current_user
import os, json
from app.models import Student, Faculty, Course, ExamSchedule
from app.api import api
from sqlalchemy import func
from app import db

@api.route('/dashboard/stats')
@login_required
def dashboard_stats():
    return jsonify({
        'students':  Student.query.count(),
        'faculty':   Faculty.query.count(),
        'courses':   Course.query.count(),
        'schedules': ExamSchedule.query.count(),
    })

@api.route('/dashboard/analytics')
@login_required
def dashboard_analytics():
    # Student distribution by department
    student_depts = db.session.query(
        Student.department, func.count(Student.id)
    ).group_by(Student.department).all()

    # Faculty distribution by department
    faculty_depts = db.session.query(
        Faculty.department, func.count(Faculty.id)
    ).group_by(Faculty.department).all()

    return jsonify({
        'student_distribution': {dept: count for dept, count in student_depts if dept},
        'faculty_distribution': {dept: count for dept, count in faculty_depts if dept}
    })

@api.route('/dashboard/security-status', methods=['GET'])
@login_required
def get_security_status():
    if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
    
    logs = []
    log_path = "logs/audit.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-20:]
            for line in reversed(lines):
                try: logs.append(json.loads(line))
                except: pass

    return jsonify({
        'database': 'Connected (SQLite WAL)',
        'csrf_protection': 'Enabled',
        'security_headers': 'Active (Talisman)',
        'rate_limiting': 'Active',
        'logs': logs
    })
