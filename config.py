import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kce_default_dev_key')
    
    # Use PostgreSQL if DATABASE_URL is set, otherwise use Supabase
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SUPABASE_URL = "postgresql://postgres:D2Nt%3F*jSEY6.x2m@db.naxwsjkozltjxxrqetrk.supabase.co:5432/postgres"
    SQLALCHEMY_DATABASE_URI = db_url or SUPABASE_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Engine Options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
    
    # SQLite-specific options
    if 'sqlite' in (db_url or 'sqlite'):
        from sqlalchemy.pool import StaticPool
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {'check_same_thread': False}
        if SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:':
            SQLALCHEMY_ENGINE_OPTIONS['poolclass'] = StaticPool
