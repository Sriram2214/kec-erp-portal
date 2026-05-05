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
        
        for code, name in depts:
            existing = Department.query.filter_by(code=code).first()
            if not existing:
                d = Department(code=code, name=name, degree_id=1)
                db.session.add(d)
                print(f"Added {code}")
            else:
                existing.name = name
                print(f"Updated {code}")
        
        db.session.commit()
        print("Done!")

if __name__ == '__main__':
    seed()
