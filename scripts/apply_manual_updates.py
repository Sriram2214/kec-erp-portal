from app import create_app, db
from sqlalchemy import text
import logging

def apply_updates():
    app = create_app()
    with app.app_context():
        # Update 1: Add columns to AcademicYear
        print("Updating AcademicYear table schema...")
        try:
            db.session.execute(text('ALTER TABLE academic_year ADD COLUMN hall_ticket_published BOOLEAN DEFAULT FALSE'))
            db.session.execute(text('ALTER TABLE academic_year ADD COLUMN results_published BOOLEAN DEFAULT FALSE'))
            db.session.commit()
            print("AcademicYear schema updated successfully.")
        except Exception as e:
            print(f"AcademicYear update failed or already updated: {e}")
            db.session.rollback()

        # Update 2: Add unique indexes
        print("Updating table constraints/indexes...")
        try:
            db.session.execute(db.text('CREATE UNIQUE INDEX IF NOT EXISTS _student_exam_idx ON attendance (student_id, exam_schedule_id)'))
            db.session.execute(db.text('CREATE UNIQUE INDEX IF NOT EXISTS _stu_exam_dummy_idx ON dummy_sticker (student_id, exam_schedule_id)'))
            db.session.execute(db.text('CREATE UNIQUE INDEX IF NOT EXISTS _dummy_course_idx ON foil_mark (dummy_number, course_id)'))
            db.session.commit()
            print("Constraints/indexes updated successfully.")
        except Exception as e:
            print(f"Constraints update failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    apply_updates()
