from flask import jsonify, request
from flask_login import login_required, current_user
from app.models import Faculty, CourseAllocation
from app import db
from app.api import api

@api.route('/faculty', methods=['GET'])
@login_required
def get_faculty():
    return jsonify([{
        'id': f.id, 'employee_id': f.employee_id,
        'name': f.name, 'department': f.department,
        'designation': f.designation or '',
        'email': f.email or '', 'phone': f.phone or '',
    } for f in Faculty.query.order_by(Faculty.department, Faculty.name).all()])

@api.route('/faculty', methods=['POST'])
@login_required
def add_faculty():
    d = request.get_json()
    if not all([d.get('employee_id'), d.get('name'), d.get('department')]):
        return jsonify({'message': 'All fields required'}), 400
    if Faculty.query.filter_by(employee_id=d['employee_id'].strip().upper()).first():
        return jsonify({'message': 'Employee ID already exists'}), 409
    f = Faculty(
        employee_id = d['employee_id'].strip().upper(),
        name        = d['name'].strip(),
        department  = d['department'].strip(),
        designation = d.get('designation', ''),
        email       = d.get('email', ''),
        phone       = d.get('phone', ''),
    )
    db.session.add(f)
    db.session.commit()
    return jsonify({'message': 'Faculty added', 'id': f.id}), 201

@api.route('/faculty/<int:fid>', methods=['DELETE'])
@login_required
def delete_faculty(fid):
    f = Faculty.query.get_or_404(fid)
    db.session.delete(f)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

@api.route('/faculty/my-courses', methods=['GET'])
@login_required
def my_courses():
    if current_user.role != 'faculty':
        return jsonify([])
    
    faculty = Faculty.query.filter_by(employee_id=current_user.username).first()
    if not faculty:
        return jsonify([])
        
    allocations = CourseAllocation.query.filter_by(faculty_id=faculty.id).all()
    res = []
    for a in allocations:
        res.append({
            'allocation_id': a.id,
            'course_code': a.course.course_code,
            'course_title': a.course.course_title,
            'batch': a.course.curriculum.batch.label,
            'section': a.section,
            'department': a.course.curriculum.department.code
        })
    return jsonify(res)
