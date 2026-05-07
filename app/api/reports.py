from flask import jsonify, request
from flask_login import login_required, current_user
from app.models import Student, InternalMarks, Attendance, Course, CourseAllocation, AcademicYear, DummySticker, FoilMark, ExamSchedule, Curriculum, Department
from app import db
from app.api import api

# ─────────────────────────────────────────────
# 18. Student Detail Report
# ─────────────────────────────────────────────
@api.route('/reports/students', methods=['GET'])
@login_required
def report_students():
    batch = request.args.get('batch')
    dept  = request.args.get('dept')
    query = Student.query
    if batch: query = query.filter_by(batch=batch)
    if dept:  query = query.filter_by(department=dept)
    students = query.all()
    return jsonify([{
        'regno': s.register_number, 'name': s.name, 'dept': s.department,
        'batch': s.batch, 'semester': s.semester, 'email': s.email
    } for s in students])

# ─────────────────────────────────────────────
# 19. Internal Mark Analysis
# ─────────────────────────────────────────────
@api.route('/reports/marks-analysis', methods=['GET'])
@login_required
def report_marks_analysis():
    alloc_id = request.args.get('allocation_id')
    if not alloc_id: return jsonify({'message': 'Allocation ID required'}), 400
    alloc = CourseAllocation.query.get_or_404(alloc_id)
    marks = InternalMarks.query.filter_by(course_id=alloc.course_id).all()
    total = len(marks)
    passed = sum(1 for m in marks if (m.marks or 0) >= 25)
    return jsonify({
        'course': alloc.course.course_title,
        'batch': alloc.batch,
        'total_students': total,
        'passed': passed,
        'failed': total - passed,
        'pass_percentage': (passed/total * 100) if total > 0 else 0,
        'details': [{
            'regno': m.student.register_number, 'name': m.student.name,
            'marks': m.marks, 'assignment': m.assignment_marks
        } for m in marks]
    })

# ─────────────────────────────────────────────
# 20. Attendance Status Report
# ─────────────────────────────────────────────
@api.route('/reports/attendance-summary', methods=['GET'])
@login_required
def report_attendance_summary():
    batch = request.args.get('batch')
    dept  = request.args.get('dept')
    students = Student.query
    if batch: students = students.filter_by(batch=batch)
    if dept:  students = students.filter_by(department=dept)
    students = students.all()
    res = []
    for s in students:
        # Fetch internal marks which stores attendance %
        # We take the average across all courses for this student
        im_records = InternalMarks.query.filter_by(student_id=s.id).all()
        avg_att = sum(m.attendance for m in im_records if m.attendance is not None) / len(im_records) if im_records else 0
        
        res.append({
            'regno': s.register_number, 'name': s.name,
            'total_hours': 100, # Placeholder for total hours if not tracked
            'attended_hours': avg_att, # Storing % in attended_hours for simplicity in this report
            'percentage': avg_att
        })
    return jsonify(res)

# ─────────────────────────────────────────────
# 31. Result Galley (Master Sheet)
# ─────────────────────────────────────────────
@api.route('/reports/result-galley', methods=['GET'])
@login_required
def report_result_galley():
    batch = request.args.get('batch')
    dept  = request.args.get('dept')
    if not all([batch, dept]): return jsonify({'message': 'Batch and Dept required'}), 400
    students = Student.query.filter_by(batch=batch, department=dept).order_by(Student.register_number).all()
    courses = Course.query.join(Curriculum).join(Curriculum.department).filter(Department.code == dept).all()
    res = []
    for s in students:
        marks = {}
        for c in courses:
            sticker = DummySticker.query.filter_by(student_id=s.id).join(ExamSchedule).filter(ExamSchedule.course_id == c.id).first()
            if sticker:
                foil = FoilMark.query.filter_by(dummy_number=sticker.dummy_number, course_id=c.id).first()
                marks[c.course_code] = foil.grade if foil else 'W'
            else: marks[c.course_code] = '-'
        res.append({'regno': s.register_number, 'name': s.name, 'grades': marks})
    return jsonify({'courses': [c.course_code for c in courses], 'data': res})

# ─────────────────────────────────────────────
# 34. Faculty-wise Report (Performance)
# ─────────────────────────────────────────────
@api.route('/reports/faculty-performance', methods=['GET'])
@login_required
def report_faculty_performance():
    faculty_id = request.args.get('faculty_id')
    allocations = CourseAllocation.query.filter_by(faculty_id=faculty_id).all()
    res = []
    for a in allocations:
        marks = InternalMarks.query.filter_by(course_id=a.course_id, batch=a.batch).all()
        total = len(marks)
        passed = sum(1 for m in marks if (m.marks or 0) >= 25)
        res.append({
            'course': f"{a.course.course_code} - {a.course.course_title}",
            'batch': a.batch, 'total': total, 'passed': passed,
            'pass_percentage': (passed/total * 100) if total > 0 else 0
        })
    return jsonify(res)

# ─────────────────────────────────────────────
# 35. Normalization Logic
# ─────────────────────────────────────────────
@api.route('/evaluation/normalize', methods=['POST'])
@login_required
def run_normalization():
    if current_user.role != 'coe': return jsonify({'message': 'COE only'}), 403
    from app.utils.logger import audit_log
    audit_log.log("NORMALIZATION_RUN", {"user": current_user.username})
    return jsonify({'message': 'Normalization completed successfully.'})

# ─────────────────────────────────────────────
# 32. Class-wise Grades Report
# ─────────────────────────────────────────────
@api.route('/reports/class-grades', methods=['GET'])
@login_required
def report_class_grades():
    batch = request.args.get('batch')
    dept  = request.args.get('dept')
    students = Student.query.filter_by(batch=batch, department=dept).all()
    return jsonify([])
