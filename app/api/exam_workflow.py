from flask import jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.api import api
from app.models import CourseRegistration, FeeClearance, Student, Course, AcademicYear
from app.utils.logger import audit_log

# ─────────────────────────────────────────────
# 15. Course Registration (Current + Backlogs)
# ─────────────────────────────────────────────
@api.route('/exam/register', methods=['POST'])
@login_required
def register_courses():
    # Only students can register themselves
    if current_user.role != 'student':
        return jsonify({'message': 'Only students can register'}), 403
        
    student = Student.query.filter_by(register_number=current_user.username).first()
    if not student: return jsonify({'message': 'Student record not found'}), 404
    
    data = request.get_json()
    course_ids = data.get('course_ids', []) # List of IDs [10, 11, 12...]
    ay_id = data.get('academic_year_id')
    
    if not ay_id: return jsonify({'message': 'Academic Year required'}), 400

    # Clear existing for this AY (to allow updates)
    CourseRegistration.query.filter_by(student_id=student.id, academic_year_id=ay_id).delete()
    
    for cid in course_ids:
        reg = CourseRegistration(
            student_id=student.id,
            course_id=cid,
            academic_year_id=ay_id,
            is_backlog=False # Logic for backlogs can be added later
        )
        db.session.add(reg)
    
    db.session.commit()
    audit_log.log("EXAM_REGISTRATION", {"student": student.register_number, "count": len(course_ids)})
    return jsonify({'message': 'Registration successful'})

@api.route('/exam/my-registrations', methods=['GET'])
@login_required
def get_my_registrations():
    student = Student.query.filter_by(register_number=current_user.username).first()
    if not student: return jsonify([])
    
    regs = CourseRegistration.query.filter_by(student_id=student.id).all()
    return jsonify([{
        'id': r.id,
        'course_code': r.course.course_code,
        'course_title': r.course.course_title,
        'ay': r.academic_year_id
    } for r in regs])

# ─────────────────────────────────────────────
# 16. Fee & Clearance Dashboard (Admin)
# ─────────────────────────────────────────────
@api.route('/exam/clearance', methods=['GET', 'POST'])
@login_required
def manage_clearance():
    if current_user.role != 'admin' and current_user.role != 'coe':
        return jsonify({'message': 'Access denied'}), 403

    if request.method == 'POST':
        d = request.get_json()
        student_id = d.get('student_id')
        ay_id = d.get('academic_year_id')
        
        clearance = FeeClearance.query.filter_by(student_id=student_id, academic_year_id=ay_id).first()
        if not clearance:
            clearance = FeeClearance(student_id=student_id, academic_year_id=ay_id)
            db.session.add(clearance)
            
        clearance.exam_fee_paid    = d.get('exam_fee_paid', clearance.exam_fee_paid)
        clearance.college_fee_paid = d.get('college_fee_paid', clearance.college_fee_paid)
        clearance.due_cleared      = d.get('due_cleared', clearance.due_cleared)
        clearance.attendance_ok    = d.get('attendance_ok', clearance.attendance_ok)
        clearance.approved         = d.get('approved', clearance.approved)
        
        if clearance.approved:
            clearance.approved_by = current_user.username
            clearance.approved_on = datetime.utcnow()
            
        db.session.commit()
        audit_log.log("CLEARANCE_UPDATE", {"student_id": student_id, "approved": clearance.approved})
        return jsonify({'message': 'Clearance updated'})

    # GET: List all students with their clearance status
    ay_id = request.args.get('ay_id')
    students = Student.query.all()
    res = []
    for s in students:
        cl = FeeClearance.query.filter_by(student_id=s.id, academic_year_id=ay_id).first()
        res.append({
            'id': s.id,
            'regno': s.register_number,
            'name': s.name,
            'dept': s.department,
            'exam_fee': cl.exam_fee_paid if cl else False,
            'college_fee': cl.college_fee_paid if cl else False,
            'attendance': cl.attendance_ok if cl else False,
            'approved': cl.approved if cl else False
        })
    return jsonify(res)
