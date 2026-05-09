from app import create_app, db
from app.models import Department, Regulation, Batch
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    print("--- Departments ---")
    for d in Department.query.all():
        print(f"'{d.code}' - {d.name}")
    
    print("\n--- Regulations ---")
    for r in Regulation.query.all():
        print(f"'{r.name}'")
        
    print("\n--- Batches ---")
    for b in Batch.query.all():
        print(f"'{b.label}'")
        
    print("\n--- All Tables ---")
    inspector = inspect(db.engine)
    for table_name in inspector.get_table_names():
        print(f"'{table_name}'")
