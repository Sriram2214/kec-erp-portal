from app import create_app, db
from app.models import User, Student

def update_passwords():
    app = create_app()
    with app.app_context():
        print("Updating student passwords to their phone numbers...")
        students = Student.query.all()
        updated_count = 0
        
        for s in students:
            user = User.query.filter_by(username=s.register_number).first()
            if not user:
                # Create user if not exists
                user = User(username=s.register_number, role='student')
                db.session.add(user)
            
            # Use phone as password, or 'password' if phone is missing
            pwd = s.phone if (s.phone and len(s.phone) >= 10) else 'password'
            user.set_password(pwd)
            updated_count += 1
            print(f"Set password for {s.register_number} to {pwd}")

        db.session.commit()
        print(f"Successfully updated {updated_count} student passwords.")

if __name__ == '__main__':
    update_passwords()
