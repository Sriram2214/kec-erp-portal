from flask import jsonify, request
from flask_login import login_required, current_user
from app.models import Course, ExamSchedule, AcademicYear, DummySticker, Attendance, Curriculum
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
            
        from app.models import Department, Batch, Regulation, Curriculum
        
        dept_code = d.get('department', 'CSE').strip().upper()
        batch_label = d.get('batch', '2023-2027').strip()
        reg_name = d.get('regulation', 'R2021').strip()
        
        # 1. Resolve Curriculum
        dept = Department.query.filter_by(code=dept_code).first()
        batch = Batch.query.filter_by(label=batch_label).first()
        reg = Regulation.query.filter_by(name=reg_name).first()
        
        if not all([dept, batch, reg]):
            return jsonify({'message': f'Master data missing for {dept_code}/{batch_label}/{reg_name}'}), 400
            
        curr = Curriculum.query.filter_by(department_id=dept.id, batch_id=batch.id, regulation_id=reg.id).first()
        if not curr:
            curr = Curriculum(department_id=dept.id, batch_id=batch.id, regulation_id=reg.id)
            db.session.add(curr)
            db.session.flush() # Get ID before commit
            
        # 2. Create Course
        c = Course(
            course_code   = code,
            course_title  = d['course_title'].strip(),
            curriculum_id = curr.id,
            semester      = int(d.get('semester', 1)),
            credits       = int(d.get('credits', 3)),
            is_lab        = d.get('is_lab', False)
        )
        db.session.add(c)
        db.session.commit()
        audit_log.log("ADD_COURSE", {"code": code, "dept": dept_code})
        return jsonify({'message': 'Course added', 'id': c.id}), 201

    from sqlalchemy.orm import joinedload
    
    # Get filters from request
    degree_id = request.args.get('degree_id')
    dept_id   = request.args.get('department_id')
    batch_id  = request.args.get('batch_id')
    reg_id    = request.args.get('regulation_id')

    query = Course.query.options(
        joinedload(Course.curriculum).joinedload(Curriculum.department),
        joinedload(Course.curriculum).joinedload(Curriculum.batch),
        joinedload(Course.curriculum).joinedload(Curriculum.regulation)
    )

    if degree_id: query = query.join(Curriculum).filter(Curriculum.degree_id == degree_id)
    if dept_id:   query = query.filter(Curriculum.department_id == dept_id)
    if batch_id:  query = query.filter(Curriculum.batch_id == batch_id)
    if reg_id:    query = query.filter(Curriculum.regulation_id == reg_id)

    courses = query.all()
    
    return jsonify([{
        'id': c.id, 
        'course_code': c.course_code,
        'course_title': c.course_title,
        'department': c.curriculum.department.code,
        'regulation': c.curriculum.regulation.name,
        'batch': c.curriculum.batch.label,
        'semester': c.semester,
        'credits': c.credits,
        'is_lab': c.is_lab
    } for c in courses])

@api.route('/courses/<int:cid>', methods=['DELETE'])
@login_required
def delete_course(cid):
    if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
    c = Course.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    audit_log.log("DELETE_COURSE", {"code": c.course_code})
    return jsonify({'message': 'Deleted'})

@api.route('/schedules', methods=['GET', 'POST'])
@login_required
def manage_schedules():
    if request.method == 'POST':
        if current_user.role != 'admin' and current_user.role != 'coe':
            return jsonify({'message': 'Access denied'}), 403
        d = request.get_json()
        if not all([d.get('course_id'), d.get('exam_date'), d.get('session')]):
            return jsonify({'message': 'Missing fields'}), 400
        
        # Check if already exists
        existing = ExamSchedule.query.filter_by(
            course_id = d['course_id'],
            exam_date = dt.datetime.strptime(d['exam_date'], '%Y-%m-%d').date()
        ).first()
        if existing: return jsonify({'message': 'Schedule already exists for this course/date'}), 409
        
        s = ExamSchedule(
            course_id        = d['course_id'],
            exam_date        = dt.datetime.strptime(d['exam_date'], '%Y-%m-%d').date(),
            session          = d['session'].upper(),
            venue            = d.get('venue', 'Main Hall'),
            academic_year_id = d.get('academic_year_id')
        )
        db.session.add(s)
        db.session.commit()
        audit_log.log("ADD_SCHEDULE", {"course_id": d['course_id'], "date": d['exam_date']})
        return jsonify({'message': 'Schedule added', 'id': s.id}), 201

    return jsonify([{
        'id': s.id,
        'course_id':    s.course_id,
        'course_code':  s.course.course_code,
        'course_title': s.course.course_title,
        'exam_date':    s.exam_date.isoformat(),
        'session':      s.session,
        'venue':        s.venue,
    } for s in ExamSchedule.query.order_by(ExamSchedule.exam_date).all()])

@api.route('/schedules/<int:sid>', methods=['DELETE'])
@login_required
def delete_schedule(sid):
    if current_user.role != 'admin' and current_user.role != 'coe':
        return jsonify({'message': 'Access denied'}), 403
    s = ExamSchedule.query.get_or_404(sid)
    db.session.delete(s)
    db.session.commit()
    audit_log.log("DELETE_SCHEDULE", {"id": sid})
    return jsonify({'message': 'Deleted'})

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
            'department':    sch.course.curriculum.department.code,
            'session':       sch.session,
            'sticker_count': sticker_count,
            'present_count': present_count,
        })

    result.sort(key=lambda x: x['course_code'])
    return jsonify(result)
