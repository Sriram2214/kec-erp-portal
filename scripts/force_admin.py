from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Force reset admin user
    user = User.query.filter_by(username='admin').first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    admin = User(username='admin', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("Admin user RE-CREATED successfully! (username: admin, password: admin123)")
