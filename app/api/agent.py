from flask import jsonify, request
from flask_login import login_required, current_user
from app.models import SystemIssue, AuditLog
from app import db
from app.api import api
import datetime as dt
import traceback

def report_system_issue(category, message, severity='warning', tb=None):
    """Internal utility for the agent to log issues"""
    issue = SystemIssue(
        category=category,
        message=message,
        severity=severity,
        traceback=tb or traceback.format_exc()
    )
    db.session.add(issue)
    db.session.commit()
    return issue

@api.route('/agent/status', methods=['GET'])
@login_required
def agent_status():
    """Returns the system health status from the agent's perspective"""
    if current_user.role not in ['admin', 'coe']:
        return jsonify({'message': 'Unauthorized'}), 403
        
    unresolved_count = SystemIssue.query.filter_by(is_resolved=False).count()
    recent_issues = SystemIssue.query.order_by(SystemIssue.timestamp.desc()).limit(5).all()
    
    return jsonify({
        'status': 'Healthy' if unresolved_count == 0 else 'Attention Required',
        'health_score': max(0, 100 - (unresolved_count * 10)),
        'unresolved_issues': unresolved_count,
        'recent_logs': [{
            'id': i.id,
            'category': i.category,
            'message': i.message,
            'severity': i.severity,
            'time': i.timestamp.isoformat()
        } for i in recent_issues]
    })

@api.route('/agent/resolve/<int:issue_id>', methods=['POST'])
@login_required
def resolve_issue(issue_id):
    if current_user.role not in ['admin', 'coe']:
        return jsonify({'message': 'Unauthorized'}), 403
    
    issue = SystemIssue.query.get_or_404(issue_id)
    issue.is_resolved = True
    db.session.commit()
    return jsonify({'message': 'Issue marked as resolved'})

@api.route('/agent/audit', methods=['GET'])
@login_required
def get_audit_logs():
    if current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
        
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return jsonify([{
        'id': l.id,
        'action': l.action,
        'details': l.details,
        'timestamp': l.timestamp.isoformat(),
        'user': l.user_id # Could join User for name
    } for l in logs])
