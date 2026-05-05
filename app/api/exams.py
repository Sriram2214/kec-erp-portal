from flask import jsonify, request
from flask_login import login_required, current_user
from app.models import Course, ExamSchedule, AcademicYear, DummySticker, Attendance
from app import db
from app.api import api
from app.utils.logger import audit_log
import datetime as dt

@api.route('/courses', methods=['GET', 'POST'])
@login_required
def manage_courses():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        d = request.get_json()
        if not all([d.get('course_code'), d.get('course_title')]):
            return jsonify({'message': 'Code and Title required'}), 400
        
        code = d['course_code'].strip().upper()
        if Course.query.filter_by(course_code=code).first():
            return jsonify({'message': 'Course code exists'}), 409
            
        c = Course(
            course_code  = code,
            course_title = d['course_title'].strip(),
            department   = d.get('department', ''),
            credits      = int(d.get('credits', 3))
        )
        db.session.add(c)
        db.session.commit()
        audit_log.log("ADD_COURSE", {"code": code})
        return jsonify({'message': 'Course added', 'id': c.id}), 201

    return jsonify([{
        'id': c.id, 'course_code': c.course_code,
        'course_title': c.course_title,
        'department': c.department, 'credits': c.credits,
    } for c in Course.query.all()])

@api.route('/courses/<int:cid>', methods=['DELETE'])
@login_required
def delete_course(cid):
    if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
    c = Course.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    audit_log.log("DELETE_COURSE", {"code": c.course_code})
    return jsonify({'message': 'Deleted'})

@api.route('/schedules', methods=['GET'])
@login_required
def get_schedules():
    return jsonify([{
        'id': s.id,
        'course_code':  s.course.course_code,
        'course_title': s.course.course_title,
        'exam_date':    s.exam_date.isoformat(),
        'session':      s.session,
    } for s in ExamSchedule.query.all()])

@api.route('/ese/courses-by-date', methods=['GET'])
@login_required
def ese_courses_by_date():
    """
    Get list of courses scheduled on a given exam date.
    ?date=2026-04-20
    Returns courses with sticker availability flag.
    """
    date_str = request.args.get('date', '').strip()
    if not date_str:
        return jsonify({'message': 'date required (YYYY-MM-DD)'}), 400

    try:
        exam_date = dt.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400

    schedules = ExamSchedule.query.filter_by(exam_date=exam_date).all()
    result = []
    for sch in schedules:
        c = sch.course
        sticker_count = DummySticker.query.filter_by(exam_schedule_id=sch.id).count()
        present_count = Attendance.query.filter_by(
            exam_schedule_id=sch.id, status='Present'
        ).count()
        result.append({
            'schedule_id':   sch.id,
            'course_code':   c.course_code,
            'course_title':  c.course_title,
            'department':    c.department,
            'session':       sch.session,
            'sticker_count': sticker_count,
            'present_count': present_count,
        })

    result.sort(key=lambda x: x['course_code'])
    return jsonify(result)
