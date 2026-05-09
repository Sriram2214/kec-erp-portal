from app import create_app, db
from sqlalchemy import text

def kill_blocking_processes():
    app = create_app()
    with app.app_context():
        print("Finding blocking processes on Supabase...")
        query = text("""
            SELECT pid, state, query, wait_event_type, wait_event 
            FROM pg_stat_activity 
            WHERE pid <> pg_backend_pid()
        """)
        results = db.session.execute(query).fetchall()
        
        if not results:
            print("No processes found.")
            return

        for pid, state, q, wet, we in results:
            print(f"Killing PID {pid}: [{state}] {q[:50]}... (Wait: {wet}/{we})")
            db.session.execute(text(f"SELECT pg_terminate_backend({pid})"))
        
        db.session.commit()
        print("Killed blocking processes.")

if __name__ == "__main__":
    kill_blocking_processes()
