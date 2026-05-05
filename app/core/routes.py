import os
from flask import send_from_directory, current_app
from app.core import core_bp

# Path to the React production build
DIST = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist')

@core_bp.route('/', defaults={'path': ''})
@core_bp.route('/<path:path>')
def serve_react(path):
    """Serve React SPA — all non-API routes return index.html."""
    # Explicitly ignore API paths
    if path.startswith('api/'):
        return None # Let Flask continue searching other blueprints
    
    # If the path matches a real static file (js/css/assets), serve it
    dist_file = os.path.join(DIST, path)
    if path and os.path.exists(dist_file):
        return send_from_directory(DIST, path)

    # Otherwise return index.html — React Router handles the rest
    index = os.path.join(DIST, 'index.html')
    if os.path.exists(index):
        return send_from_directory(DIST, 'index.html')

    # Build not found — dev mode message
    return (
        '<h2>KEC ERP — Development Mode</h2>'
        '<p>Run <code>cd frontend && npm run build</code> to generate the production build.</p>'
        '<p>Or run <code>npm run dev</code> and access <a href="http://localhost:3000">http://localhost:3000</a></p>'
    ), 200
