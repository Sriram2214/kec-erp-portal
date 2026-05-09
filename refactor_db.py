import os
from sqlalchemy import text
from app import create_app, db
from app.models import Degree, Department, Batch, Regulation, AcademicYear, User

def refactor():
    app = create_app()
    with app.app_context():
        print("Refactoring database schema on Supabase...")
        
        # Drop dependent tables first
        tables_to_drop = [
            'foil_mark', 'dummy_sticker', 'attendance', 'exam_schedule', 
            'internal_marks', 'class_attendance', 'class_timetable', 
            'course_allocation', 'course_registration', 'course', 'curriculum',
            'department', 'degree', 'batch', 'regulation'
        ]
        
        for table in tables_to_drop:
            try:
                db.session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"Dropped {table}")
            except Exception as e:
                print(f"Error dropping {table}: {e}")
        
        db.session.commit()
        
        # Recreate all tables
        db.create_all()
        print("Tables recreated successfully.")

        # Seed master data if empty
        if Degree.query.count() == 0:
            db.session.add_all([Degree(name='BE'), Degree(name='B.Tech'), Degree(name='ME'), Degree(name='PhD')])
            db.session.commit()
            print("Degrees seeded.")

        if Department.query.count() == 0:
            be = Degree.query.filter_by(name='BE').first()
            bt = Degree.query.filter_by(name='B.Tech').first()
            depts = [
                ('CSE', 'Computer Science and Engineering', be.id),
                ('ECE', 'Electronics and Communication Engineering', be.id),
                ('MECH', 'Mechanical Engineering', be.id),
                ('BME', 'Biomedical Engineering', be.id),
                ('RAA', 'Robotics and Automation', be.id),
                ('IT', 'Information Technology', bt.id),
                ('AI&DS', 'Artificial Intelligence and Data Science', bt.id),
                ('AIML', 'Artificial Intelligence and Machine Learning', bt.id)
            ]
            for code, name, did in depts:
                db.session.add(Department(code=code, name=name, degree_id=did))
            db.session.commit()
            print("Departments seeded.")

        if Batch.query.count() == 0:
            # UG and PG Batches from image
            batches = [
                '2021-2025', '2022-2026', '2023-2027', '2024-2028', '2025-2029', '2026-2030', # UG
                '2023-2025', '2024-2026', '2025-2027', '2026-2028' # PG
            ]
            for b in batches:
                db.session.add(Batch(label=b))
            db.session.commit()
            print("Batches seeded.")

        if Regulation.query.count() == 0:
            regs = ['R2017', 'R2019', 'R2021', 'R2022', 'R2023', 'R2024']
            for r in regs:
                db.session.add(Regulation(name=r))
            db.session.commit()
            print("Regulations seeded.")

        if AcademicYear.query.count() == 0:
            # Academic Years from image
            ays = [
                ('2021-2022', 'ODD'), ('2021-2022', 'EVEN'),
                ('2022-2023', 'ODD'), ('2022-2023', 'EVEN'),
                ('2023-2024', 'ODD'), ('2023-2024', 'EVEN'),
                ('2024-2025', 'ODD', True), ('2024-2025', 'EVEN'),
                ('2025-2026', 'ODD'), ('2025-2026', 'EVEN'),
                ('2026-2027', 'ODD'), ('2026-2027', 'EVEN')
            ]
            for ay_data in ays:
                label = ay_data[0]
                sem = ay_data[1]
                is_curr = ay_data[2] if len(ay_data) > 2 else False
                db.session.add(AcademicYear(label=label, semester=sem, is_current=is_curr))
            db.session.commit()
            print("Academic Years seeded.")

if __name__ == "__main__":
    refactor()
