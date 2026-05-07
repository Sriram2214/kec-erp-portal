from app import create_app, db
from app.models import Course

app = create_app()
with app.app_context():
    total = Course.query.count()
    no_curr = Course.query.filter_by(curriculum_id=None).count()
    print(f"Total courses: {total}")
    print(f"Courses with no curriculum: {no_curr}")
    if no_curr > 0:
        sample = Course.query.filter_by(curriculum_id=None).first()
        print(f"Sample broken course: {sample.course_code} - {sample.course_title}")
