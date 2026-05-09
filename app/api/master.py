from flask import jsonify, request
from flask_login import login_required, current_user
from app import db
from app.api import api
from app.models import Degree, Department, Batch, Regulation, AcademicYear
from app.utils.logger import audit_log

@api.route('/master/degrees', methods=['GET', 'POST'])
@login_required
def manage_degrees():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        data = request.get_json()
        name = data.get('name', '').strip()
        if not name: return jsonify({'message': 'Name required'}), 400
        if Degree.query.filter_by(name=name).first(): return jsonify({'message': 'Degree exists'}), 409
        
        deg = Degree(name=name)
        db.session.add(deg)
        db.session.commit()
        audit_log.log("ADD_DEGREE", {"name": name})
        return jsonify({'message': 'Degree added', 'id': deg.id}), 201

    return jsonify([{'id': d.id, 'name': d.name} for d in Degree.query.all()])

@api.route('/master/departments', methods=['GET', 'POST'])
@login_required
def manage_departments():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        data = request.get_json()
        code = data.get('code', '').strip().upper()
        name = data.get('name', '').strip()
        if not code or not name: return jsonify({'message': 'Code and Name required'}), 400
        if Department.query.filter_by(code=code).first(): return jsonify({'message': 'Dept code exists'}), 409
        
        dept = Department(code=code, name=name)
        db.session.add(dept)
        db.session.commit()
        audit_log.log("ADD_DEPARTMENT", {"code": code, "name": name})
        return jsonify({'message': 'Department added', 'id': dept.id}), 201

    return jsonify([{'id': d.id, 'code': d.code, 'name': d.name} for d in Department.query.all()])

@api.route('/master/batches', methods=['GET', 'POST'])
@login_required
def manage_batches():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        data = request.get_json()
        label = data.get('label', '').strip() # e.g. "2021-2025"
        if not label: return jsonify({'message': 'Label required'}), 400
        if Batch.query.filter_by(label=label).first(): return jsonify({'message': 'Batch exists'}), 409
        
        batch = Batch(label=label)
        db.session.add(batch)
        db.session.commit()
        audit_log.log("ADD_BATCH", {"label": label})
        return jsonify({'message': 'Batch added', 'id': batch.id}), 201

    return jsonify([{'id': b.id, 'label': b.label} for b in Batch.query.all()])

@api.route('/master/regulations', methods=['GET', 'POST'])
@login_required
def manage_regulations():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        data = request.get_json()
        name = data.get('name', '').strip() # e.g. "R2021"
        if not name: return jsonify({'message': 'Name required'}), 400
        if Regulation.query.filter_by(name=name).first(): return jsonify({'message': 'Regulation exists'}), 409
        
        reg = Regulation(name=name)
        db.session.add(reg)
        db.session.commit()
        audit_log.log("ADD_REGULATION", {"name": name})
        return jsonify({'message': 'Regulation added', 'id': reg.id}), 201

    return jsonify([{'id': r.id, 'name': r.name} for r in Regulation.query.all()])

@api.route('/master/academic-years', methods=['GET', 'POST'])
@login_required
def manage_ay():
    if request.method == 'POST':
        if current_user.role != 'admin': return jsonify({'message': 'Access denied'}), 403
        data = request.get_json()
        label = data.get('label', '').strip() # e.g. "2024-25"
        sem   = data.get('semester', 'Odd')
        curr  = data.get('is_current', False)
        
        if curr:
            # Set others to false
            AcademicYear.query.update({AcademicYear.is_current: False})
            
        ay = AcademicYear(label=label, semester=sem, is_current=curr)
        db.session.add(ay)
        db.session.commit()
        audit_log.log("ADD_ACADEMIC_YEAR", {"label": label, "sem": sem})
        return jsonify({'message': 'Academic Year added', 'id': ay.id}), 201

    return jsonify([{
        'id': a.id, 'label': a.label, 'semester': a.semester, 'is_current': a.is_current
    } for a in AcademicYear.query.all()])

@api.route('/master', methods=['GET'])
@login_required
def get_all_master():
    depts = [{'id': d.id, 'code': d.code, 'name': d.name} for d in Department.query.all()]
    degrees = [{'id': d.id, 'name': d.name} for d in Degree.query.all()]
    batches = [{'id': b.id, 'label': b.label} for b in Batch.query.all()]
    regs = [{'id': r.id, 'name': r.name} for r in Regulation.query.all()]
    ays = [{'id': a.id, 'label': a.label, 'semester': a.semester, 'is_current': a.is_current} for a in AcademicYear.query.all()]

    # Fallback for Vercel/Empty DB
    if not depts:
        depts = [
            {'id': 1, 'code': 'AI&DS', 'name': 'Artificial Intelligence and Data Science'},
            {'id': 2, 'code': 'AIML', 'name': 'Artificial Intelligence and Machine Learning'},
            {'id': 3, 'code': 'BME', 'name': 'Biomedical Engineering'},
            {'id': 4, 'code': 'CSE', 'name': 'Computer Science and Engineering'},
            {'id': 5, 'code': 'ECE', 'name': 'Electronics and Communication Engineering'},
            {'id': 6, 'code': 'IT', 'name': 'Information Technology'},
            {'id': 7, 'code': 'MECH', 'name': 'Mechanical Engineering'},
            {'id': 8, 'code': 'CIVIL', 'name': 'Civil Engineering'},
            {'id': 9, 'code': 'RAA', 'name': 'Robotics and Automation'}
        ]
    if not degrees:
        degrees = [
            {'id': 1, 'name': 'B.E'},
            {'id': 2, 'name': 'B.TECH'},
            {'id': 3, 'name': 'M.E'},
            {'id': 4, 'name': 'PhD.'}
        ]
    if not batches:
        batches = [
            {'id': 1, 'label': '2021-2025'}, {'id': 2, 'label': '2022-2026'},
            {'id': 3, 'label': '2023-2027'}, {'id': 4, 'label': '2024-2028'},
            {'id': 5, 'label': '2025-2029'}, {'id': 6, 'label': '2026-2030'},
            {'id': 7, 'label': '2023-2025'}, {'id': 8, 'label': '2024-2026'},
            {'id': 9, 'label': '2025-2027'}, {'id': 10, 'label': '2026-2028'}
        ]
    if not regs:
        regs = [{'id': 1, 'name': 'R2021'}, {'id': 2, 'name': 'R2019'}]
    if not ays:
        ays = [
            {'id': 1, 'label': '2021-2022', 'semester': 'ODD', 'is_current': False},
            {'id': 2, 'label': '2022-2023', 'semester': 'ODD', 'is_current': False},
            {'id': 3, 'label': '2023-2024', 'semester': 'ODD', 'is_current': False},
            {'id': 4, 'label': '2024-2025', 'semester': 'ODD', 'is_current': True},
            {'id': 5, 'label': '2025-2026', 'semester': 'ODD', 'is_current': False},
            {'id': 6, 'label': '2026-2027', 'semester': 'ODD', 'is_current': False}
        ]

    return jsonify({
        'departments': depts,
        'degrees': degrees,
        'batches': batches,
        'regulations': regs,
        'academic_years': ays
    })
