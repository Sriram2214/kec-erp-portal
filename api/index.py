import sys
import os
import sqlalchemy

# Add root directory to sys.path so 'app' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app import db

app = create_app()

with app.app_context():
    try:
        # Check if tables exist. If not, this is likely a fresh Vercel instance using /tmp/app.db
        engine = db.engine
        inspector = sqlalchemy.inspect(engine)
        if not inspector.has_table("user"):
            from app.api.init import init_db
            # Run the initialization within a test request context so jsonify doesn't fail
            with app.test_request_context('/api/init-db'):
                init_db()
            print("Auto-initialized database master data successfully.", flush=True)
    except Exception as e:
        print(f"Error during auto-initialization: {e}", flush=True)

application = app
