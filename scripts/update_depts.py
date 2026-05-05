from app import create_app, db
from app.models import Degree, Department

app = create_app()

with app.app_context():
    # Ensure ME degree exists
    me_degree = Degree.query.filter_by(name='ME').first()
    if not me_degree:
        me_degree = Degree(name='ME')
        db.session.add(me_degree)
        db.session.flush()

    be_degree = Degree.query.filter_by(name='BE').first()
    
    # We will use 'SH' (Science and Humanities) or 'PhD' for the basic sciences, 
    # but since it doesn't specify, let's just map them to BE or a generic 'SH' degree.
    # Let's create 'SH' (Science & Humanities) degree just in case
    sh_degree = Degree.query.filter_by(name='S&H').first()
    if not sh_degree:
        sh_degree = Degree(name='S&H')
        db.session.add(sh_degree)
        db.session.flush()

    depts_to_add_update = [
        ('AIDS', 'Artificial Intelligence & Data Science', be_degree.id),
        ('AIML', 'Artificial Intelligence & Machine Learning', be_degree.id),
        ('BME',  'Biomedical Engineering', be_degree.id),
        ('CSE',  'Computer Science and Engineering', be_degree.id),
        ('ECE',  'Electronics and Communication Engineering', be_degree.id),
        ('IT',   'Information Technology', be_degree.id),
        ('MECH', 'Mechanical Engineering', be_degree.id),
        ('RAA',  'Robotics and Automation', be_degree.id),
        ('ME-CSE','M.E Computer Science and Engineering', me_degree.id),
        ('ENG',  'Department of English', sh_degree.id),
        ('CHEM', 'Department of Chemistry', sh_degree.id),
        ('PHY',  'Department of Physics', sh_degree.id),
        ('MATH', 'Department of Mathematics', sh_degree.id)
    ]

    for code, name, deg_id in depts_to_add_update:
        dept = Department.query.filter_by(code=code).first()
        if dept:
            dept.name = name
            dept.degree_id = deg_id
        else:
            db.session.add(Department(code=code, name=name, degree_id=deg_id))
            
    db.session.commit()
    print("Departments updated successfully!")
