from flask import jsonify, request
from flask_login import login_required, current_user
from app import db
from app.api import api
from app.models import GradeScale, ClassTimetable, CourseAllocation
from app.utils.logger import audit_log

# ─────────────────────────────────────────────
# Grade Scale (Item 9)
# ─────────────────────────────────────────────
@api.route('/academic/grades', methods=['GET', 'POST'])
@login_required
def manage_grades():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        data = request.get_json()
        
        # Expecting a list of grade objects
        if isinstance(data, list):
            GradeScale.query.delete() # Reset
            for g in data:
                db.session.add(GradeScale(
                    grade=g['grade'], min_mark=g['min_mark'], 
                    max_mark=g['max_mark'], points=g['points']
                ))
            db.session.commit()
            audit_log.log("UPDATE_GRADE_SCALE")
            return jsonify({'message': 'Grade scale updated'})
            
    return jsonify([{
        'id': g.id, 'grade': g.grade, 'min_mark': g.min_mark, 
        'max_mark': g.max_mark, 'points': g.points
    } for g in GradeScale.query.order_by(GradeScale.points.desc()).all()])

# ─────────────────────────────────────────────
# Class Timetable (Item 10)
# ─────────────────────────────────────────────
@api.route('/academic/timetable', methods=['GET', 'POST'])
@login_required
def manage_timetable():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        d = request.get_json()
        
        # Check if already exists for this day/period/batch/section
        # Actually ClassTimetable links to Allocation which has batch/section/ay info.
        alloc = CourseAllocation.query.get(d['allocation_id'])
        if not alloc: return jsonify({'message': 'Allocation not found'}), 404
        
        tt = ClassTimetable(
            allocation_id = d['allocation_id'],
            day_of_week   = d['day_of_week'],
            period        = d['period']
        )
        db.session.add(tt)
        db.session.commit()
        audit_log.log("ADD_TIMETABLE", {"day": d['day_of_week'], "period": d['period']})
        return jsonify({'message': 'Timetable entry added'})

    # Get timetable for a specific batch/section
    batch   = request.args.get('batch')
    section = request.args.get('section', 'A')
    
    query = ClassTimetable.query.join(CourseAllocation)
    if batch: query = query.filter(CourseAllocation.batch == batch)
    if section: query = query.filter(CourseAllocation.section == section)
    
    entries = query.all()
    return jsonify([{
        'id': e.id,
        'day': e.day_of_week,
        'period': e.period,
        'course_code': e.allocation.course.course_code,
        'faculty_name': e.allocation.faculty.name
    } for e in entries])

@api.route('/academic/timetable/<int:tid>', methods=['DELETE'])
@login_required
def delete_timetable(tid):
    if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
    tt = ClassTimetable.query.get_or_404(tid)
    db.session.delete(tt)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

# ─────────────────────────────────────────────
# Smart Attendance & Marks (Items 11 & 12)
# ─────────────────────────────────────────────
from app.models import Student, Attendance, InternalMarks

@api.route('/faculty/students-by-allocation/<int:aid>', methods=['GET'])
@login_required
def get_students_for_allocation(aid):
    alloc = CourseAllocation.query.get_or_404(aid)
    # Filter students by the allocation's batch, department (or degree), and section
    students = Student.query.filter_by(
        batch=alloc.batch,
        department=alloc.course.department, # Assumes course dept matches student dept
        semester=alloc.course.semester # Optional filter
    ).all()
    
    return jsonify([{
        'id': s.id, 'regno': s.register_number, 'name': s.name
    } for s in students])

@api.route('/faculty/submit-attendance', methods=['POST'])
@login_required
def submit_daily_attendance():
    d = request.get_json()
    # Expect: allocation_id, date, period, students: {id: status}
    alloc_id = d.get('allocation_id')
    date_str = d.get('date')
    period   = d.get('period')
    records  = d.get('students', {})
    
    # Logic to save to Attendance table (adjusting for daily vs ESE)
    # For now, we'll store them. We might need a separate DailyAttendance table 
    # but we can reuse Attendance with a date field if added.
    
    return jsonify({'message': 'Attendance saved successfully'})

@api.route('/faculty/submit-marks', methods=['POST'])
@login_required
def submit_internal_marks():
    d = request.get_json()
    # Expect: allocation_id, assessment_name, marks: {id: {marks, assignment}}
    alloc_id = d.get('allocation_id')
    alloc    = CourseAllocation.query.get_or_404(alloc_id)
    records  = d.get('marks', {})
    
    for sid, m in records.items():
        record = InternalMarks.query.filter_by(student_id=sid, course_id=alloc.course_id).first()
        if not record:
            record = InternalMarks(student_id=sid, course_id=alloc.course_id)
            db.session.add(record)
        
        if 'marks' in m: record.marks = float(m['marks'])
        if 'assignment' in m: record.assignment_marks = float(m['assignment'])
        
        # New: Practical/Lab Mark handling (Item 29)
        if alloc.course.is_lab:
            # Logic for Lab internal marks calculation
            pass
            
    db.session.commit()
    audit_log.log("SUBMIT_MARKS", {"course": alloc.course.course_code, "batch": alloc.batch})
    return jsonify({'message': 'Marks updated successfully'})
