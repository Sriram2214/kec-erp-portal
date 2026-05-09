"""
Migration: Create semester_dummy_allocation table
Run: python migrate_semester_dummy.py
"""
from app import create_app, db
from app.models import SemesterDummyAllocation

app = create_app()
with app.app_context():
    db.create_all()
    print("[OK] semester_dummy_allocation table created (or already exists).")
    count = SemesterDummyAllocation.query.count()
    print(f"[INFO] Current allocations in table: {count}")
