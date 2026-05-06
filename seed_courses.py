"""
Seed comprehensive KEC R2021 courses for all depts & semesters.
Run once: python seed_courses.py
"""
from app import create_app, db
from app.models import Course

app = create_app()

COURSES = [
    # ── Common / GE courses (all depts) ──────────────────────────────
    ('GE241203', 'Universal Human Values',                    'COMMON', 6, 2, False),
    ('GE2412',   'Universal Human Values',                    'COMMON', 6, 2, False),
    ('GE3751',   'Professional Ethics and HRD',               'COMMON', 7, 2, False),
    ('MA3151',   'Matrices and Calculus',                     'COMMON', 1, 4, False),
    ('MA3251',   'Statistics and Numerical Methods',          'COMMON', 3, 4, False),
    ('MA3351',   'Transforms and Partial Differential Eq.',   'COMMON', 5, 4, False),
    ('HS3151',   'Professional English I',                    'COMMON', 1, 2, False),
    ('HS3251',   'Professional English II',                   'COMMON', 2, 2, False),
    ('PH3151',   'Engineering Physics',                       'COMMON', 1, 4, False),
    ('CY3151',   'Engineering Chemistry',                     'COMMON', 1, 4, False),
    ('BE3251',   'Basic Electrical & Electronics Engg.',      'COMMON', 2, 4, False),
    ('GE3251',   'Engineering Graphics',                      'COMMON', 2, 4, False),
    ('GE3151',   'Problem Solving and Python Programming',    'COMMON', 1, 4, False),

    # ── CSE ───────────────────────────────────────────────────────────
    ('CS3301',   'Data Structures',                           'CSE',    3, 4, False),
    ('CS3401',   'Algorithms',                                'CSE',    4, 4, False),
    ('CS3491',   'Artificial Intelligence and ML',            'CSE',    5, 4, False),
    ('CS3501',   'Computer Networks',                         'CSE',    5, 4, False),
    ('CS3591',   'Compiler Design',                           'CSE',    5, 4, False),
    ('CS3601',   'Software Engineering',                      'CSE',    6, 4, False),
    ('CS3651',   'Mobile Application Development',            'CSE',    6, 4, False),
    ('CS8651',   'Internet Programming',                      'CSE',    6, 4, False),
    ('CS8691',   'Artificial Intelligence',                   'CSE',    6, 4, False),
    ('CS3701',   'Cloud Computing',                           'CSE',    7, 4, False),
    ('CS3791',   'Cyber Security',                            'CSE',    7, 4, False),

    # ── IT ────────────────────────────────────────────────────────────
    ('IT3301',   'Data Structures and Algorithms',            'IT',     3, 4, False),
    ('IT3401',   'Application Development',                   'IT',     4, 4, False),
    ('IT3501',   'Information Security',                      'IT',     5, 4, False),
    ('IT3601',   'Service Oriented Architecture',             'IT',     6, 4, False),
    ('IT8601',   'Computational Intelligence',                'IT',     6, 4, False),
    ('IT3701',   'Internet of Things',                        'IT',     7, 4, False),

    # ── AI&DS ─────────────────────────────────────────────────────────
    ('AD3301',   'Statistical Foundations of Data Science',   'AI&DS',  3, 4, False),
    ('AD3401',   'Machine Learning',                          'AI&DS',  4, 4, False),
    ('AD3501',   'Deep Learning',                             'AI&DS',  5, 4, False),
    ('AD3601',   'Big Data Analytics',                        'AI&DS',  6, 4, False),
    ('AD3701',   'Natural Language Processing',               'AI&DS',  7, 4, False),

    # ── AIML ──────────────────────────────────────────────────────────
    ('AM3301',   'Foundations of Machine Learning',           'AIML',   3, 4, False),
    ('AM3401',   'Deep Learning Architectures',               'AIML',   4, 4, False),
    ('AM3501',   'Computer Vision',                           'AIML',   5, 4, False),
    ('AM3601',   'Reinforcement Learning',                    'AIML',   6, 4, False),

    # ── ECE ───────────────────────────────────────────────────────────
    ('EC3301',   'Signals and Systems',                       'ECE',    3, 4, False),
    ('EC3401',   'VLSI Design',                               'ECE',    4, 4, False),
    ('EC3501',   'Digital Communication',                     'ECE',    5, 4, False),
    ('EC3601',   'Antenna and Wave Propagation',              'ECE',    6, 4, False),
    ('EC8691',   'Microprocessors and Microcontrollers',      'ECE',    6, 4, False),
    ('EC3701',   'Wireless Communication',                    'ECE',    7, 4, False),

    # ── MECH ──────────────────────────────────────────────────────────
    ('ME3301',   'Engineering Thermodynamics',                'MECH',   3, 4, False),
    ('ME3401',   'Manufacturing Technology II',               'MECH',   4, 4, False),
    ('ME3501',   'Heat and Mass Transfer',                    'MECH',   5, 4, False),
    ('ME3601',   'Design of Machine Elements',                'MECH',   6, 4, False),
    ('EE8601',   'Solid State Drives',                        'MECH',   6, 4, False),
    ('ME3701',   'CAD/CAM',                                   'MECH',   7, 4, False),

    # ── CIVIL ─────────────────────────────────────────────────────────
    ('CE3301',   'Mechanics of Solids',                       'CIVIL',  3, 4, False),
    ('CE3401',   'Structural Analysis',                       'CIVIL',  4, 4, False),
    ('CE3501',   'Design of Reinforced Concrete Structures',  'CIVIL',  5, 4, False),
    ('CE3601',   'Foundation Engineering',                    'CIVIL',  6, 4, False),
    ('CE3701',   'Construction Management',                   'CIVIL',  7, 4, False),

    # ── BME ───────────────────────────────────────────────────────────
    ('BM3301',   'Biomedical Instrumentation',                'BME',    3, 4, False),
    ('BM3401',   'Medical Imaging',                           'BME',    4, 4, False),
    ('BM3501',   'Biosignal Processing',                      'BME',    5, 4, False),
    ('BM3601',   'Rehabilitation Engineering',                'BME',    6, 4, False),

    # ── RAA ───────────────────────────────────────────────────────────
    ('RA3301',   'Robotics Kinematics and Dynamics',          'RAA',    3, 4, False),
    ('RA3401',   'Robot Programming',                         'RAA',    4, 4, False),
    ('RA3501',   'Automation and Control',                    'RAA',    5, 4, False),
    ('RA3601',   'Autonomous Systems',                        'RAA',    6, 4, False),

    # ── Lab courses ───────────────────────────────────────────────────
    ('CS3311',   'Data Structures Lab',                       'CSE',    3, 2, True),
    ('CS3411',   'Algorithms Lab',                            'CSE',    4, 2, True),
    ('IT3311',   'Application Development Lab',               'IT',     3, 2, True),
    ('AD3311',   'Data Science Lab',                          'AI&DS',  3, 2, True),
    ('EC3311',   'Electronic Circuits Lab',                   'ECE',    3, 2, True),
    ('ME3311',   'Engineering Practices Lab',                 'MECH',   3, 2, True),
]

def seed():
    with app.app_context():
        added = 0
        skipped = 0
        for code, title, dept, sem, credits, is_lab in COURSES:
            if Course.query.filter(Course.course_code.ilike(code)).first():
                skipped += 1
                continue
            db.session.add(Course(
                course_code=code, course_title=title,
                department=dept, semester=sem,
                credits=credits, is_lab=is_lab, regulation='R2021'
            ))
            added += 1
        db.session.commit()
        print(f'Done! Added {added} courses, skipped {skipped} duplicates.')
        print(f'Total courses in DB: {Course.query.count()}')

if __name__ == '__main__':
    seed()
