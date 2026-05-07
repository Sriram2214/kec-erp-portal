from app import db, create_app
from app.models import Department

def seed():
    app = create_app()
    with app.app_context():
        depts = [
            ('AI&DS', 'Artificial Intelligence and Data Science'),
            ('AIML', 'Artificial Intelligence and Machine Learning'),
            ('BME', 'Biomedical Engineering'),
            ('CSE', 'Computer Science and Engineering'),
            ('ECE', 'Electronics and Communication Engineering'),
            ('IT', 'Information Technology'),
            ('MECH', 'Mechanical Engineering'),
            ('RAA', 'Robotics and Automation')
        ]
        
        from app.models import Degree
        deg = Degree.query.first()
        if not deg:
            deg = Degree()
            deg.name = 'B.E'
            db.session.add(deg); db.session.commit()

        for code, name in depts:
            existing = Department.query.filter_by(code=code).first()
            if not existing:
                d = Department()
                d.code = code
                d.name = name
                d.degree_id = deg.id
                db.session.add(d)
                print(f"Added {code}")
            else:
                existing.name = name
                print(f"Updated {code}")
        
        db.session.commit()
        print("Done!")

if __name__ == '__main__':
    seed()
