import random
from app import create_app, db
from app.models import Student, User, Department, AcademicYear

def seed_large_scale():
    app = create_app()
    with app.app_context():
        print("Scaling system to 2000+ students...")
        
        # 1. Ensure departments exist
        depts = Department.query.all()
        if not depts:
            print("No departments found. Please run main seed first.")
            return

        ay = AcademicYear.query.filter_by(is_current=True).first()
        
        # 2. Bulk creation
        # We'll use 5 departments, 400 students each = 2000 students
        student_count = 0
        
        for dept in depts[:5]: # Take up to 5 departments
            print(f"Adding 400 students for {dept.code}...")
            
            # Base Reg No for this dept: 210822104001, 210822105001, etc.
            base_reg = 210822100000 + (depts.index(dept) * 1000)
            
            new_students = []
            new_users = []
            
            for i in range(1, 401):
                reg_no = str(base_reg + i)
                phone = f"9{random.randint(100000000, 999999999)}"
                
                # Check if exists
                if not Student.query.filter_by(register_number=reg_no).first():
                    s = Student(
                        register_number=reg_no,
                        name=f"STUDENT {reg_no}",
                        department=dept.code,
                        semester=random.choice([2, 4, 6, 8]),
                        batch='2021-2025',
                        degree='B.E.',
                        regulation='2021',
                        dob='15/05/2003',
                        phone=phone,
                        academic_year=ay.id if ay else 1
                    )
                    new_students.append(s)
                    
                    # User login
                    u = User(username=reg_no, role='student')
                    u.set_password(phone)
                    new_users.append(u)

                    student_count += 1
            
            db.session.add_all(new_students)
            db.session.add_all(new_users)
            db.session.commit()
            print(f"Committed {len(new_students)} students for {dept.code}")

        print(f"\nSuccessfully scaled to {student_count} students with unique Logins (Reg No + Phone)!")

if __name__ == '__main__':
    seed_large_scale()
