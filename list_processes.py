from app import create_app, db
from sqlalchemy import text

def list_all_processes():
    app = create_app()
    with app.app_context():
        print("Listing all active processes on Supabase...")
        query = text("""
            SELECT pid, state, query, wait_event_type, wait_event 
            FROM pg_stat_activity 
            WHERE state = 'active' AND pid <> pg_backend_pid()
        """)
        results = db.session.execute(query).fetchall()
        for pid, state, q, wet, we in results:
            print(f"PID {pid}: [{state}] {q[:100]}... (Wait: {wet}/{we})")

if __name__ == "__main__":
    list_all_processes()
