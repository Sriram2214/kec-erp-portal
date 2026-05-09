"""
KCE ERP — Curriculum + Student Registration Engine
====================================================

This script implements the MANDATORY registration pipeline:

  Curriculum → Courses → Students → CourseRegistration

Rules:
- A student is registered to a course ONLY if their
  (department_code, regulation, batch) matches the course's curriculum.
- course_code alone is NEVER globally unique.
- All ESE workflows use ONLY CourseRegistration.
"""

import csv
import sys
from app import create_app, db
from app.models import (
    Curriculum, Course, Student, CourseRegistration,
    Degree, Department, Batch, Regulation
)

# ===========================================================
# MAPPING: CSV dept full name → DB Department name
# ===========================================================
DEPT_FULL_TO_NAME = {
    "B.E. Biomedical Engineering":              "Biomedical Engineering",
    "B.E. Computer Science and Engineering":    "Computer Science and Engineering",
    "B.E. Computer Science and Engineering (Artificial Intelligence and Machine Learning)":
                                                "Computer Science and Engineering (Artificial Intelligence and Machine Learning)",
    "B.E. Electronics and Communication Engineering": "Electronics and Communication Engineering",
    "B.E. Mechanical Engineering":              "Mechanical Engineering",
    "B.E. Robotics and Automation":             "Robotics and Automation",
    "B.Tech. Artificial Intelligence and Data Science": "Artificial Intelligence and Data Science",
    "B.Tech. Information Technology":           "Information Technology",
    "M.E. Computer Science and Engineering":    "Computer Science and Engineering",
}

DEPT_FULL_TO_DEGREE = {
    "B.E. Biomedical Engineering":              "BE",
    "B.E. Computer Science and Engineering":    "BE",
    "B.E. Computer Science and Engineering (Artificial Intelligence and Machine Learning)": "BE",
    "B.E. Electronics and Communication Engineering": "BE",
    "B.E. Mechanical Engineering":              "BE",
    "B.E. Robotics and Automation":             "BE",
    "B.Tech. Artificial Intelligence and Data Science": "B.Tech",
    "B.Tech. Information Technology":           "B.Tech",
    "M.E. Computer Science and Engineering":    "ME",
}


def run_engine(course_csv_path: str):
    app = create_app()
    with app.app_context():
        print("=" * 60, flush=True)
        print("KCE Curriculum Registration Engine", flush=True)
        print("=" * 60, flush=True)

        # --------------------------------------------------
        # PHASE 1: Load all curricula from DB into a lookup
        # --------------------------------------------------
        print("\nPHASE 1: Loading curricula from DB...", flush=True)
        all_curricula = (
            db.session.query(Curriculum)
            .join(Degree)
            .join(Department)
            .join(Batch)
            .join(Regulation)
            .all()
        )

        # Key: (degree_name, dept_name, batch_label, reg_name) → curriculum
        curriculum_map = {}
        for c in all_curricula:
            key = (c.degree.name, c.department.name, c.batch.label, c.regulation.name)
            curriculum_map[key] = c

        print(f"  Loaded {len(curriculum_map)} curriculum entries.", flush=True)

        # --------------------------------------------------
        # PHASE 2: Load all students grouped by (dept_code, batch, regulation)
        # --------------------------------------------------
        print("\nPHASE 2: Loading students from DB...", flush=True)
        all_students = db.session.query(Student).all()
        # Group: (dept_code, batch_label, reg_name) → [student_ids]
        student_group = {}
        for s in all_students:
            key = (s.department, s.batch, s.regulation)
            student_group.setdefault(key, []).append(s.id)

        print(f"  Loaded {len(all_students)} students across {len(student_group)} groups.", flush=True)

        # --------------------------------------------------
        # PHASE 3: Process course CSV
        # --------------------------------------------------
        print(f"\nPHASE 3: Processing {course_csv_path}...", flush=True)

        courses_added = 0
        regs_added = 0
        skipped_curriculum = set()

        with open(course_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                dept_full = row['DEPARTMENT'].strip()
                batch_raw = row['BATCH'].strip().replace(' ', '')
                reg_raw   = 'R' + row['REGULATION'].strip()
                sem       = int(row['SEM'])
                code      = row['COURSE CODE'].strip().upper()
                name      = row['COURSE NAME'].strip()
                credits   = int(float(row.get('CREDITS', '0') or '0'))

                degree_name = DEPT_FULL_TO_DEGREE.get(dept_full)
                dept_name   = DEPT_FULL_TO_NAME.get(dept_full)

                if not degree_name or not dept_name:
                    # Unknown dept format — try strip prefix fallback
                    for prefix, deg in [("B.E.", "BE"), ("B.Tech.", "B.Tech"), ("M.E.", "ME")]:
                        if dept_full.startswith(prefix):
                            degree_name = deg
                            dept_name   = dept_full[len(prefix):].strip()
                            break

                if not degree_name:
                    print(f"  SKIP (unknown dept): {dept_full}", flush=True)
                    continue

                curr_key = (degree_name, dept_name, batch_raw, reg_raw)

                if curr_key not in curriculum_map:
                    if curr_key not in skipped_curriculum:
                        print(f"  CURRICULUM NOT FOUND: {curr_key}", flush=True)
                        skipped_curriculum.add(curr_key)
                    continue

                curriculum = curriculum_map[curr_key]
                dept_code  = curriculum.department.code

                # Step 3a: Ensure course exists
                course = Course.query.filter_by(
                    course_code=code,
                    curriculum_id=curriculum.id
                ).first()

                if not course:
                    course = Course(
                        course_code=code,
                        course_title=name,
                        curriculum_id=curriculum.id,
                        semester=sem,
                        credits=credits
                    )
                    db.session.add(course)
                    db.session.flush()
                    courses_added += 1

                # Step 3b: Register students
                # Students who belong to THIS curriculum:
                # dept_code, batch_raw, reg_raw
                student_key = (dept_code, batch_raw, reg_raw)
                student_ids = student_group.get(student_key, [])

                if not student_ids:
                    # Debug: try reg without 'R' prefix
                    student_key_plain = (dept_code, batch_raw, row['REGULATION'].strip())
                    student_ids = student_group.get(student_key_plain, [])

                if student_ids:
                    # Get already registered student IDs for this course
                    existing = set(
                        r[0] for r in db.session.query(CourseRegistration.student_id)
                        .filter(CourseRegistration.course_id == course.id).all()
                    )

                    new_count = 0
                    for sid in student_ids:
                        if sid not in existing:
                            db.session.add(CourseRegistration(
                                student_id=sid,
                                course_id=course.id
                            ))
                            regs_added += 1
                            new_count += 1

                    if new_count:
                        print(f"  {code} [{batch_raw}|{reg_raw}|{dept_code}] -> +{new_count} students", flush=True)

                # Commit every 20 courses to stay within connection time
                if courses_added % 20 == 0 and courses_added > 0:
                    db.session.commit()
                    print(f"  >>> Committed. Courses: {courses_added}, Regs: {regs_added}", flush=True)

        db.session.commit()
        print("\n" + "=" * 60, flush=True)
        print(f"DONE! Courses added: {courses_added} | Registrations added: {regs_added}", flush=True)
        print(f"Skipped curricula: {len(skipped_curriculum)}", flush=True)
        if skipped_curriculum:
            for k in sorted(skipped_curriculum):
                print(f"  MISSING: {k}", flush=True)
        print("=" * 60, flush=True)


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'original_course_details.csv'
    run_engine(csv_path)
