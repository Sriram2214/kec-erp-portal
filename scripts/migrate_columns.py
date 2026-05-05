from app import create_app, db

app = create_app()
with app.app_context():
    student_cols = [
        ("degree",     "VARCHAR(20) DEFAULT 'BE'"),
        ("regulation", "VARCHAR(20) DEFAULT 'R2021'"),
        ("semester",   "INTEGER DEFAULT 1"),
        ("email",      "VARCHAR(120) DEFAULT ''"),
        ("phone",      "VARCHAR(15) DEFAULT ''"),
        ("dob",        "VARCHAR(12) DEFAULT ''"),
    ]
    for col, defn in student_cols:
        try:
            db.session.execute(db.text(f"ALTER TABLE student ADD COLUMN {col} {defn}"))
            print(f"Added student.{col}")
        except Exception as e:
            msg = str(e).lower()
            if "duplicate column" in msg:
                print(f"Already exists: student.{col}")
            else:
                print(f"Error student.{col}: {e}")

    faculty_cols = [
        ("designation", "VARCHAR(80) DEFAULT ''"),
        ("email",       "VARCHAR(120) DEFAULT ''"),
        ("phone",       "VARCHAR(15) DEFAULT ''"),
    ]
    for col, defn in faculty_cols:
        try:
            db.session.execute(db.text(f"ALTER TABLE faculty ADD COLUMN {col} {defn}"))
            print(f"Added faculty.{col}")
        except Exception as e:
            msg = str(e).lower()
            if "duplicate column" in msg:
                print(f"Already exists: faculty.{col}")
            else:
                print(f"Error faculty.{col}: {e}")

    course_cols = [
        ("semester",   "INTEGER"),
        ("regulation", "VARCHAR(20) DEFAULT 'R2021'"),
        ("is_lab",     "BOOLEAN DEFAULT 0"),
    ]
    for col, defn in course_cols:
        try:
            db.session.execute(db.text(f"ALTER TABLE course ADD COLUMN {col} {defn}"))
            print(f"Added course.{col}")
        except Exception as e:
            msg = str(e).lower()
            if "duplicate column" in msg:
                print(f"Already exists: course.{col}")
            else:
                print(f"Error course.{col}: {e}")

    db.session.commit()
    print("Migration complete!")
