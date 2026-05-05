from flask import jsonify, request
from flask_login import login_required, current_user
from app import db
from app.api import api
from app.models import Faculty, Course, CourseAllocation, AcademicYear, Batch
from app.utils.logger import audit_log

@api.route('/allocations', methods=['GET', 'POST'])
@login_required
def manage_allocations():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        d = request.get_json()
        
        # Required: faculty_id, course_id, batch, academic_year_id, section
        if not all([d.get('faculty_id'), d.get('course_id'), d.get('batch'), d.get('academic_year_id')]):
            return jsonify({'message': 'Missing required fields'}), 400
            
        alloc = CourseAllocation(
            faculty_id       = d['faculty_id'],
            course_id        = d['course_id'],
            batch            = d['batch'],
            academic_year_id = d['academic_year_id'],
            section          = d.get('section', 'A')
        )
        db.session.add(alloc)
        db.session.commit()
        
        f = Faculty.query.get(d['faculty_id'])
        c = Course.query.get(d['course_id'])
        audit_log.log("ADD_ALLOCATION", {"faculty": f.name, "course": c.course_code, "batch": d['batch']})
        
        return jsonify({'message': 'Allocation created', 'id': alloc.id}), 201

    allocs = CourseAllocation.query.all()
    return jsonify([{
        'id': a.id,
        'faculty_name': a.faculty.name,
        'course_code':  a.course.course_code,
        'course_title': a.course.course_title,
        'batch': a.batch,
        'section': a.section,
        'academic_year': a.academic_year.label if a.academic_year else 'N/A'
    } for a in allocs])

@api.route('/allocations/<int:aid>', methods=['DELETE'])
@login_required
def delete_allocation(aid):
    if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
    a = CourseAllocation.query.get_or_404(aid)
    db.session.delete(a)
    db.session.commit()
    audit_log.log("DELETE_ALLOCATION", {"id": aid})
    return jsonify({'message': 'Deleted'})
