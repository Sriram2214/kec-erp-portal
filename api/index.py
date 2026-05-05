import sys
import os

# Add root directory to sys.path so 'app' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import create_app
    app = create_app()
    application = app
except Exception as e:
    import traceback
    from flask import Flask, jsonify
    app = Flask(__name__)
    @app.route('/<path:path>')
    @app.route('/')
    def error_page(path=''):
        return f"<h1>Backend Crash Detected</h1><pre>{traceback.format_exc()}</pre>", 500
    application = app
