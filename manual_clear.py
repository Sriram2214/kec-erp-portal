from app import create_app, db
from app.models import Student, CourseRegistration, Attendance, DummySticker, FoilMark
from sqlalchemy import text

def manual_clear():
    app = create_app()
    with app.app_context():
        print("Clearing transactional tables...")
        for table in ['foil_mark', 'dummy_sticker', 'attendance', 'course_registration']:
            db.session.execute(text(f"DELETE FROM {table}"))
            db.session.commit()
            print(f"  {table} cleared.")
            
        print("Clearing students in small chunks...")
        while True:
            # Get 100 IDs
            ids = [s.id for s in Student.query.limit(100).all()]
            if not ids:
                break
            
            db.session.execute(text(f"DELETE FROM student WHERE id IN ({','.join(map(str, ids))})"))
            db.session.commit()
            print(f"  Deleted {len(ids)} students...", end='\r')
        
        print("\nAll students cleared.")

if __name__ == "__main__":
    manual_clear()
