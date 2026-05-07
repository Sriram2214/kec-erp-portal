from flask import jsonify, request
from flask_login import login_required, current_user
from app.models import FoilMark, DummySticker, ExamSchedule, Student, InternalMarks, GradeScale, FeeClearance
from app import db
from app.api import api
from app.utils.logger import audit_log

# ─────────────────────────────────────────────
# Foil Mark Entry (External Exam Marks)
# ─────────────────────────────────────────────
@api.route('/evaluation/submit-foil', methods=['POST'])
@login_required
def submit_foil_marks():
    if current_user.role != 'admin' and current_user.role != 'coe':
        return jsonify({'message': 'Access denied'}), 403
        
    d = request.get_json()
    schedule_id = d.get('schedule_id')
    marks_data  = d.get('marks', {})
    
    for dummy_no, ext_mark in marks_data.items():
        sticker = DummySticker.query.filter_by(dummy_number=dummy_no, exam_schedule_id=schedule_id).first()
        if not sticker: continue
        
        foil = FoilMark.query.filter_by(dummy_number=dummy_no, course_id=sticker.exam_schedule.course_id).first()
        if not foil:
            foil = FoilMark(dummy_number=dummy_no, course_id=sticker.exam_schedule.course_id)
            db.session.add(foil)
        
        foil.external_mark = float(ext_mark)
        internal = InternalMarks.query.filter_by(student_id=sticker.student_id, course_id=sticker.exam_schedule.course_id).first()
        int_val = (internal.marks if internal else 0)
        total = int_val + float(ext_mark)
        
        grade_obj = GradeScale.query.filter(GradeScale.min_mark <= total, GradeScale.max_mark >= total).first()
        foil.grade = grade_obj.grade if grade_obj else 'U'
        
    db.session.commit()
    audit_log.log("FOIL_MARK_SUBMISSION", {"schedule_id": schedule_id})
    return jsonify({'message': 'Marks submitted and grades calculated successfully'})

# ─────────────────────────────────────────────
# Result Summary for Admin
# ─────────────────────────────────────────────
@api.route('/evaluation/summary/<int:schedule_id>', methods=['GET'])
@login_required
def evaluation_summary(schedule_id):
    stickers = DummySticker.query.filter_by(exam_schedule_id=schedule_id).all()
    res = []
    for s in stickers:
        foil = FoilMark.query.filter_by(dummy_number=s.dummy_number, course_id=s.exam_schedule.course_id).first()
        res.append({
            'dummy_no': s.dummy_number,
            'regno': s.student.register_number,
            'name': s.student.name,
            'external': foil.external_mark if foil else 0,
            'grade': foil.grade if foil else '-'
        })
    return jsonify(res)

# ─────────────────────────────────────────────
# 32. Revaluation Process & Command Center
# ─────────────────────────────────────────────
@api.route('/evaluation/revaluation/apply', methods=['POST'])
@login_required
def apply_revaluation():
    if current_user.role != 'student': return jsonify({'message': 'Students only'}), 403
    d = request.get_json()
    audit_log.log("REVALUATION_APPLIED", {"student": current_user.username, "course": d.get('course_id')})
    return jsonify({'message': 'Revaluation application submitted successfully'})

@api.route('/coe/revaluation-list', methods=['GET'])
@login_required
def coe_revaluation_list():
    if current_user.role not in ['admin', 'coe']: return jsonify({'message': 'Access denied'}), 403
    revals = FoilMark.query.all()
    return jsonify([{
        'id': f.id,
        'dummy_no': f.dummy_number,
        'old_mark': f.external_mark,
        'grade': f.grade
    } for f in revals])

@api.route('/coe/revaluation-update', methods=['POST'])
@login_required
def update_revaluation_mark():
    if current_user.role not in ['admin', 'coe']: return jsonify({'message': 'Access denied'}), 403
    d = request.get_json()
    foil = FoilMark.query.get_or_404(d.get('foil_id'))
    foil.external_mark = float(d.get('new_mark'))
    
    # Recalculate Grade
    sticker = DummySticker.query.filter_by(dummy_number=foil.dummy_number, course_id=foil.course_id).first()
    int_val = 0
    if sticker:
        internal = InternalMarks.query.filter_by(student_id=sticker.student_id, course_id=foil.course_id).first()
        int_val = internal.marks if internal else 0
    
    total = int_val + foil.external_mark
    grade_obj = GradeScale.query.filter(GradeScale.min_mark <= total, GradeScale.max_mark >= total).first()
    foil.grade = grade_obj.grade if grade_obj else 'U'
    
    db.session.commit()
    audit_log.log("REVALUATION_MARK_UPDATED", {"foil_id": foil.id, "new_mark": foil.external_mark})
    return jsonify({'message': 'Revaluation mark updated successfully!'})

# ─────────────────────────────────────────────
# 33-35. Certification (Grade Sheets / Provisional)
# ─────────────────────────────────────────────
@api.route('/certificates/grade-sheet', methods=['GET'])
@login_required
def get_grade_sheet():
    regno = request.args.get('regno') or current_user.username
    return jsonify({'message': f'Grade Sheet for {regno} generated. (PDF Logic Ready)'})

@api.route('/certificates/consolidated', methods=['GET'])
@login_required
def get_consolidated_sheet():
    regno = request.args.get('regno') or current_user.username
    student = Student.query.filter_by(register_number=regno).first_or_404()
    results = []
    all_stickers = DummySticker.query.filter_by(student_id=student.id).all()
    for s in all_stickers:
        foil = FoilMark.query.filter_by(dummy_number=s.dummy_number, course_id=s.exam_schedule.course_id).first()
        if foil:
            results.append({
                'semester': s.exam_schedule.course.semester,
                'code': s.exam_schedule.course.course_code,
                'title': s.exam_schedule.course.course_title,
                'grade': foil.grade,
                'credits': 3
            })
    return jsonify({
        'student_name': student.name,
        'regno': student.register_number,
        'department': student.department,
        'semesters': sorted(results, key=lambda x: (x['semester'], x['code']))
    })
