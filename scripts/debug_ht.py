from app import create_app
from app.models import Student, ExamSchedule, Course, AcademicYear

app = create_app()
with app.app_context():
    regno = '210822205098'
    s = Student.query.filter_by(register_number=regno).first()
    if not s:
        print("Student not found!")
    else:
        ay = AcademicYear.query.filter_by(is_current=True).first()
        print(f"Student: {s.name}, Dept: {s.department}, Sem: {s.semester}")
        print(f"Current AY: {ay.label if ay else 'None'}")
        
        # Exact query used in API
        schedules = ExamSchedule.query.join(Course).filter(
            Course.department == s.department,
            Course.semester == s.semester,
            ExamSchedule.academic_year_id == (ay.id if ay else None)
        ).all()
        print(f"Schedules found with AY: {len(schedules)}")

        # Query without AY
        schedules_no_ay = ExamSchedule.query.join(Course).filter(
            Course.department == s.department,
            Course.semester == s.semester
        ).all()
        print(f"Schedules found WITHOUT AY: {len(schedules_no_ay)}")
