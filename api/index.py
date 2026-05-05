
from app import create_app

app = create_app()

# This is for Vercel to pick up the app object
# Vercel looks for 'app' or 'application'
application = app
