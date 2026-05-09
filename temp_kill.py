from app import create_app, db
from sqlalchemy import text
app = create_app()
with app.app_context():
    query = text("""
        SELECT pid, state, query 
        FROM pg_stat_activity 
        WHERE state = 'idle in transaction' OR query ILIKE '%course_registration%';
    """)
    results = db.session.execute(query).fetchall()
    for pid, state, q in results:
        print(f'Found PID {pid}: [{state}]')
        try:
            db.session.execute(text(f'SELECT pg_terminate_backend({pid})'))
            print('Killed')
        except Exception as e:
            pass
    db.session.commit()
