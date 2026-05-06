import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kce_default_dev_key')
    
    # Force Supabase URL (Ignore Vercel environment variables which might be stuck on sqlite)
    SUPABASE_URL = "postgresql://postgres:D2Nt%3F*jSEY6.x2m@db.naxwsjkozltjxxrqetrk.supabase.co:5432/postgres"
    SQLALCHEMY_DATABASE_URI = SUPABASE_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Engine Options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
    

