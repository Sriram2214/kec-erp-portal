from app import create_app, db
from app.models import Curriculum

app = create_app()
with app.app_context():
    total = Curriculum.query.count()
    no_dept = Curriculum.query.filter_by(department_id=None).count()
    print(f"Total curriculums: {total}")
    print(f"Curriculums with no department: {no_dept}")
    
    currs = Curriculum.query.all()
    broken = []
    for c in currs:
        if not c.department:
            broken.append(c.id)
    print(f"Curriculums with broken department relationship: {len(broken)}")
