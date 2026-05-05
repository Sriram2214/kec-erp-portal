from app import create_app, db
from app.models import User
import os

app = create_app()
with app.app_context():
    print(f"Current Users: {User.query.count()}")
    for u in User.query.all():
        print(f" - {u.username} ({u.role})")
    
    print("\nResetting admin...")
    admin = User.query.filter_by(username='admin').first()
    if admin:
        db.session.delete(admin)
        db.session.commit()
    
    new_admin = User(username='admin', role='admin')
    new_admin.set_password('admin123')
    db.session.add(new_admin)
    db.session.commit()
    
    print(f"Final Users: {User.query.count()}")
    print(f"Admin hash: {User.query.filter_by(username='admin').first().password_hash}")
