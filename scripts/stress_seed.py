"""
Stress test seed — generates 3000 students + 200 faculty
Run: venv\Scripts\python stress_seed.py
"""
import random, time
from app import create_app, db
from app.models import Student, Faculty

DEPTS   = ['AIDS','AIML','BME','CSE','ECE','IT','MECH','RAA']
BATCHES = ['2021-2025','2022-2026','2023-2027','2024-2028']
REGS    = ['R2021','R2021','R2021','R2019']  # weighted towards R2021
DESIGS  = ['Professor','Associate Professor','Assistant Professor',
           'Assistant Professor','Assistant Professor','Senior Lecturer']

FIRST = ['Arun','Priya','Karthik','Deepa','Suresh','Nithya','Vijay','Anitha',
         'Ramesh','Kavitha','Senthil','Lakshmi','Murugan','Selvi','Bala','Geetha',
         'Ganesh','Meena','Vinoth','Revathi','Ashok','Sowmya','Dinesh','Saranya',
         'Harish','Pooja','Rajan','Indira','Kumar','Padma','Sathish','Radha',
         'Manoj','Shanthi','Prakash','Uma','Rajesh','Divya','Mohan','Rekha']

LAST  = ['Kumar','Raj','Devi','Selvam','Muthu','Rajan','Krishnan','Sundaram',
         'Perumal','Natarajan','Murugesan','Subramanian','Arumugam','Pillai',
         'Pandian','Shanmugam','Venkatesan','Gopal','Ramasamy','Palani']

app = create_app()
with app.app_context():
    start = time.time()

    # ── 3000 Students ─────────────────────────────────────────────────────
    existing = set(r[0] for r in db.session.execute(
        db.text("SELECT register_number FROM student")).fetchall())

    students = []
    count = 0
    for dept_idx, dept in enumerate(DEPTS):
        per_dept = 3000 // len(DEPTS)   # ~375 per dept
        for batch in BATCHES:
            year_str = batch[:4][2:]     # "21" from "2021-2025"
            per_batch = per_dept // len(BATCHES)  # ~93 per batch
            for i in range(1, per_batch + 1):
                reg = f"{year_str}{dept}{str(i).zfill(3)}"
                if reg in existing:
                    continue
                yr  = BATCHES.index(batch) + 1
                sem = yr * 2             # approx current sem
                students.append(Student(
                    register_number = reg,
                    name            = f"{random.choice(FIRST)} {random.choice(LAST)}",
                    department      = dept,
                    degree          = 'BE',
                    batch           = batch,
                    academic_year   = yr,
                    semester        = sem,
                    regulation      = random.choice(REGS),
                    email           = f"{reg.lower()}@kec.ac.in",
                    phone           = f"9{random.randint(100000000,999999999)}",
                    dob             = f"200{random.randint(1,6)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                ))
                existing.add(reg)
                count += 1

        # Batch commit per dept
        if students:
            db.session.bulk_save_objects(students)
            db.session.commit()
            print(f"  [OK] {dept}: {count} students committed")
            students = []

    total_students = Student.query.count()
    print(f"\n[DONE] Students in DB: {total_students}")

    # ── 200 Faculty ───────────────────────────────────────────────────────
    existing_emp = set(r[0] for r in db.session.execute(
        db.text("SELECT employee_id FROM faculty")).fetchall())

    faculty_batch = []
    fcount = 0
    per_dept_f = 200 // len(DEPTS)   # 25 per dept

    for dept in DEPTS:
        for i in range(1, per_dept_f + 1):
            emp_id = f"KEC{dept}{str(i).zfill(3)}"
            if emp_id in existing_emp:
                continue
            faculty_batch.append(Faculty(
                employee_id = emp_id,
                name        = f"{random.choice(FIRST)} {random.choice(LAST)}",
                department  = dept,
                designation = random.choice(DESIGS),
                email       = f"{emp_id.lower()}@kec.ac.in",
                phone       = f"9{random.randint(100000000,999999999)}",
            ))
            existing_emp.add(emp_id)
            fcount += 1

    db.session.bulk_save_objects(faculty_batch)
    db.session.commit()

    total_faculty = Faculty.query.count()
    elapsed = round(time.time() - start, 2)

    print(f"[DONE] Faculty in DB:   {total_faculty}")
    print(f"[TIME] Total time:      {elapsed}s")
    print(f"\nDB now has {total_students} students + {total_faculty} staff")
