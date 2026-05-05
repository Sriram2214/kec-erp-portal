import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kce_default_dev_key')
    
    # Use PostgreSQL if DATABASE_URL is set, otherwise use SQLite
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    # Vercel Read-Only Fix: Use /tmp for SQLite if in production
    if os.environ.get('VERCEL') == '1':
        tmp_db = '/tmp/app.db'
        seeded_db = os.path.join(basedir, 'instance', 'app_seeded.db')
        import shutil
        if not os.path.exists(tmp_db) and os.path.exists(seeded_db):
            shutil.copy2(seeded_db, tmp_db)
        SQLALCHEMY_DATABASE_URI = db_url or f'sqlite:///{tmp_db}'
    else:
        SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Engine Options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'connect_args': {'check_same_thread': False} if 'sqlite' in (db_url or 'sqlite') else {}
    }
