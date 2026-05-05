from flask import render_template, request, jsonify
from app import db
import logging

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Resource not found', 'status': 404}), 404
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        logging.error(f"SERVER ERROR: {error} | Path: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({'message': 'Internal server error', 'status': 500}), 500
        return render_template('errors/500.html', title='Internal Server Error'), 500

    @app.errorhandler(429)
    def ratelimit_handler(e):
        logging.warning(f"Rate limit exceeded by {request.remote_addr} on {request.path}")
        return jsonify({'message': 'Too many requests. Please try again later.', 'status': 429}), 429
