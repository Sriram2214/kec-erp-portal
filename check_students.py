from app import create_app
from app.models import Student, CourseRegistration
app = create_app()
with app.app_context():
    print(f"Current Student Count: {Student.query.count()}")
    print(f"Current Registration Count: {CourseRegistration.query.count()}")
    print("\n--- Sample Students ---")
    for s in Student.query.limit(5).all():
        print(f"{s.register_number} - {s.name}")
