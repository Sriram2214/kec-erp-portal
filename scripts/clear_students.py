from app import create_app, db
from app.models import Student, ClassAttendance, InternalMarks, CourseRegistration, FeeClearance, HallTicket, Attendance, DummySticker

app = create_app()

with app.app_context():
    print("Clearing student records and related data...")
    # Delete related tables first due to foreign keys
    db.session.query(ClassAttendance).delete()
    db.session.query(InternalMarks).delete()
    db.session.query(CourseRegistration).delete()
    db.session.query(FeeClearance).delete()
    db.session.query(HallTicket).delete()
    db.session.query(Attendance).delete()
    db.session.query(DummySticker).delete()
    
    # Delete all students
    num_deleted = db.session.query(Student).delete()
    db.session.commit()
    print(f"Successfully deleted {num_deleted} students.")
