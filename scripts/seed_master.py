from app import create_app, db
from app.models import Degree, Department, Batch, Regulation, AcademicYear

app = create_app()

with app.app_context():
    # ── Degrees ─────────────────────────────────────
    degrees_data = ['BE', 'B.Tech', 'ME', 'PhD']
    for d in degrees_data:
        if not Degree.query.filter_by(name=d).first():
            db.session.add(Degree(name=d))
    db.session.commit()

    # ── Departments ─────────────────────────────────
    be_degree = Degree.query.filter_by(name='BE').first()
    if be_degree:
        dept_data = [
            ('CSE',  'Computer Science and Engineering'),
            ('ECE',  'Electronics and Communication Engineering'),
            ('MECH', 'Mechanical Engineering'),
            ('IT',   'Information Technology'),
            ('AIDS', 'Artificial Intelligence and Data Science'),
            ('AIML', 'Artificial Intelligence and Machine Learning'),
            ('BME',  'Biomedical Engineering'),
            ('RAA',  'Robotics and Automation')
        ]
        for code, name in dept_data:
            if not Department.query.filter_by(code=code).first():
                db.session.add(Department(code=code, name=name, degree_id=be_degree.id))
        db.session.commit()

    # ── Batches ─────────────────────────────────────
    batches_data = ['2021-2025', '2022-2026', '2023-2027', '2024-2028']
    for b in batches_data:
        if not Batch.query.filter_by(label=b).first():
            db.session.add(Batch(label=b))
    db.session.commit()

    # ── Regulations ─────────────────────────────────
    regs_data = ['R2021', 'R2019', 'R2017']
    for r in regs_data:
        if not Regulation.query.filter_by(name=r).first():
            db.session.add(Regulation(name=r))
    db.session.commit()

    # ── Academic Years ──────────────────────────────
    ay_data = [
        ('2024-2025', 'ODD', False),
        ('2024-2025', 'EVEN', True),
        ('2025-2026', 'ODD', False)
    ]
    for label, sem, is_cur in ay_data:
        if not AcademicYear.query.filter_by(label=label, semester=sem).first():
            db.session.add(AcademicYear(label=label, semester=sem, is_current=is_cur))
    db.session.commit()

    print("Master data successfully seeded!")
