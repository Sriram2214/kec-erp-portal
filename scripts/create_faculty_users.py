from app import create_app, db
from app.models import User, Faculty

app = create_app()

with app.app_context():
    faculties = Faculty.query.all()
    count = 0
    for f in faculties:
        if not User.query.filter_by(username=f.employee_id).first():
            u = User(username=f.employee_id, role='faculty')
            u.set_password('faculty123')
            db.session.add(u)
            count += 1
    
    db.session.commit()
    print(f"Created {count} faculty user accounts with password 'faculty123'")
