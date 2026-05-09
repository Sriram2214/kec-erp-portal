from app import create_app, db
from app.models import Student, CourseRegistration, Attendance, DummySticker, InternalMarks, ClassAttendance, FoilMark, HallTicket, FeeClearance

def wipe_student_data():
    app = create_app()
    with app.app_context():
        print("Wiping all student-related sample data...")
        
        # Order matters due to potential foreign keys (though SQLite might not enforce it, good practice)
        FoilMark.query.delete()
        DummySticker.query.delete()
        Attendance.query.delete()
        InternalMarks.query.delete()
        ClassAttendance.query.delete()
        CourseRegistration.query.delete()
        HallTicket.query.delete()
        FeeClearance.query.delete()
        Student.query.delete()
        
        db.session.commit()
        print("Successfully removed all student records and related exam data.")
        print("Master data (Departments, Batches, Courses) is still intact.")

if __name__ == "__main__":
    wipe_student_data()
