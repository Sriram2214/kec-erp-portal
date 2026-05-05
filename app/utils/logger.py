import logging
import os
import json
from datetime import datetime
from flask_login import current_user

class AuditLogger:
    def __init__(self, log_dir="logs"):
        # On Vercel, the file system is read-only except for /tmp
        if os.environ.get('VERCEL') == '1' or not os.access(".", os.W_OK):
            log_dir = "/tmp/logs"
            
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            self.logger = logging.getLogger("audit")
            self.logger.setLevel(logging.INFO)
            
            handler = logging.FileHandler(os.path.join(log_dir, "audit.log"), encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
        except OSError:
            # Fallback to console logging if file system is completely locked
            self.logger = logging.getLogger("audit_fallback")
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)

    def log(self, action, details=None):
        """
        Structured logging for admin/faculty actions.
        """
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user.username if current_user.is_authenticated else "anonymous",
            "role": current_user.role if current_user.is_authenticated and hasattr(current_user, 'role') else "unknown",
            "action": action,
            "details": details or {}
        }
        self.logger.info(json.dumps(payload))

# Global instance
audit_log = AuditLogger()
