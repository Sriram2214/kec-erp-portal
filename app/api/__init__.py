from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

# Import modules to register routes
from app.api import auth, master, students, faculty, exams, ese, staff, dashboard, allocations, academic_ops, exam_workflow, reports, coe, evaluation
