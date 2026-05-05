from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role          = db.Column(db.String(20), nullable=False, default='staff')  # admin / staff / coe

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ─────────────────────────────────────────────
# Master Data
# ─────────────────────────────────────────────
class Degree(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)  # BE, B.Tech, ME, PhD
    departments = db.relationship('Department', backref='degree', lazy=True)

class Department(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    code      = db.Column(db.String(10), unique=True, nullable=False)   # CSE, ECE …
    name      = db.Column(db.String(100), nullable=False)
    degree_id = db.Column(db.Integer, db.ForeignKey('degree.id'), nullable=False)

class Regulation(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)  # R2021, R2019 …

class AcademicYear(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    label      = db.Column(db.String(20), unique=True, nullable=False) # 2023-24, 2024-25
    semester   = db.Column(db.String(10), nullable=False)              # ODD / EVEN
    is_current = db.Column(db.Boolean, default=False)
    
    # Visibility Controls
    hall_ticket_published = db.Column(db.Boolean, default=False)
    results_published     = db.Column(db.Boolean, default=False)

    def __repr__(self): return f'<AY {self.label} {self.semester}>'

class Batch(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), unique=True, nullable=False)  # 2021-2025

# ─────────────────────────────────────────────
# Students & Faculty
# ─────────────────────────────────────────────
class Student(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.String(20), unique=True, nullable=False)
    name            = db.Column(db.String(100), nullable=False)
    department      = db.Column(db.String(50), nullable=False)   # dept code
    batch           = db.Column(db.String(20), nullable=False)
    academic_year   = db.Column(db.Integer, nullable=False)      # 1 / 2 / 3 / 4
    degree          = db.Column(db.String(20), default='BE')
    regulation      = db.Column(db.String(20), default='R2021')
    semester        = db.Column(db.Integer, default=1)
    email           = db.Column(db.String(120))
    phone           = db.Column(db.String(15))
    dob             = db.Column(db.String(12))
    result_published = db.Column(db.Boolean, default=False)

class Faculty(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    department  = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(80))
    email       = db.Column(db.String(120))
    phone       = db.Column(db.String(15))

# ─────────────────────────────────────────────
# Courses
# ─────────────────────────────────────────────
class Course(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    course_code  = db.Column(db.String(20), unique=True, nullable=False)
    course_title = db.Column(db.String(150), nullable=False)
    department   = db.Column(db.String(50), nullable=False)
    credits      = db.Column(db.Integer)
    semester     = db.Column(db.Integer)
    regulation   = db.Column(db.String(20), default='R2021')
    is_lab       = db.Column(db.Boolean, default=False)

class CourseAllocation(db.Model):
    """Faculty ↔ Course mapping per batch & academic year"""
    id               = db.Column(db.Integer, primary_key=True)
    faculty_id       = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    batch            = db.Column(db.String(20), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))
    section          = db.Column(db.String(5), default='A')

    faculty      = db.relationship('Faculty', backref=db.backref('allocations', lazy=True))
    course       = db.relationship('Course',  backref=db.backref('allocations', lazy=True))
    academic_year = db.relationship('AcademicYear')

class GradeScale(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    grade      = db.Column(db.String(5), nullable=False) # O, A+, A, B+...
    min_mark   = db.Column(db.Integer, nullable=False)
    max_mark   = db.Column(db.Integer, nullable=False)
    points     = db.Column(db.Integer, nullable=False)

class ClassTimetable(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    allocation_id = db.Column(db.Integer, db.ForeignKey('course_allocation.id'), nullable=False)
    day_of_week   = db.Column(db.String(10), nullable=False) # Monday, Tuesday...
    period        = db.Column(db.Integer, nullable=False)      # 1, 2, 3, 4, 5, 6, 7, 8
    
    allocation    = db.relationship('CourseAllocation', backref=db.backref('periods', lazy=True))

# ─────────────────────────────────────────────
# Attendance
# ─────────────────────────────────────────────
class ClassAttendance(db.Model):
    """Day-wise class attendance entry"""
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date             = db.Column(db.Date, nullable=False)
    session          = db.Column(db.String(5), default='FN')   # FN / AN
    status           = db.Column(db.String(10), default='P')   # P / A / OD
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))

    student      = db.relationship('Student', backref=db.backref('class_attendance', lazy=True))
    course       = db.relationship('Course',  backref=db.backref('class_attendance', lazy=True))

# ─────────────────────────────────────────────
# Internal Marks
# ─────────────────────────────────────────────
class InternalMarks(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    ia1              = db.Column(db.Float, default=0)
    ia2              = db.Column(db.Float, default=0)
    ia3              = db.Column(db.Float, default=0)
    assignment_marks = db.Column(db.Float, default=0)
    marks            = db.Column(db.Float, default=0)   # computed best of 2
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))

    student = db.relationship('Student', backref=db.backref('internal_marks', lazy=True))
    course  = db.relationship('Course',  backref=db.backref('internal_marks', lazy=True))

# ─────────────────────────────────────────────
# End Semester Exam
# ─────────────────────────────────────────────
class ExamSchedule(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    exam_date        = db.Column(db.Date, nullable=False)
    session          = db.Column(db.String(5), nullable=False)   # FN / AN
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))
    venue            = db.Column(db.String(50))

    course       = db.relationship('Course', backref=db.backref('schedules', lazy=True))
    academic_year = db.relationship('AcademicYear')

class CourseRegistration(db.Model):
    """Student-wise course registration — current + backlogs"""
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))
    is_backlog       = db.Column(db.Boolean, default=False)
    registered_on    = db.Column(db.DateTime, default=datetime.utcnow)

    student      = db.relationship('Student', backref=db.backref('registrations', lazy=True))
    course       = db.relationship('Course',  backref=db.backref('registrations', lazy=True))

class FeeClearance(db.Model):
    """Exam fee + due clearance + hall ticket approval"""
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))
    exam_fee_paid    = db.Column(db.Boolean, default=False)
    college_fee_paid = db.Column(db.Boolean, default=False)
    due_cleared      = db.Column(db.Boolean, default=False)
    attendance_ok    = db.Column(db.Boolean, default=False)
    approved         = db.Column(db.Boolean, default=False)
    approved_by      = db.Column(db.String(64))
    approved_on      = db.Column(db.DateTime)
    remarks          = db.Column(db.String(200))

    student = db.relationship('Student', backref=db.backref('fee_clearance', lazy=True))

class HallTicket(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))
    generated_at     = db.Column(db.DateTime, default=datetime.utcnow)
    generated_by     = db.Column(db.String(64))

    student = db.relationship('Student', backref=db.backref('hall_tickets', lazy=True))

from sqlalchemy import UniqueConstraint

class Attendance(db.Model):
    """ESE Exam attendance"""
    __table_args__ = (UniqueConstraint('student_id', 'exam_schedule_id', name='_student_exam_uc'),)
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    exam_schedule_id = db.Column(db.Integer, db.ForeignKey('exam_schedule.id'), nullable=False)
    status           = db.Column(db.String(20), default='Present')  # Present / Absent / Malpractice

    student      = db.relationship('Student',      backref=db.backref('attendances', lazy=True))
    exam_schedule = db.relationship('ExamSchedule', backref=db.backref('attendances', lazy=True))

class DummySticker(db.Model):
    __table_args__ = (db.UniqueConstraint('student_id', 'exam_schedule_id', name='_stu_exam_dummy_uc'),)
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    exam_schedule_id = db.Column(db.Integer, db.ForeignKey('exam_schedule.id'), nullable=False)
    dummy_number     = db.Column(db.String(50), nullable=False)
    foil_number      = db.Column(db.String(50), nullable=False)

    student       = db.relationship('Student',      backref=db.backref('dummy_stickers', lazy=True))
    exam_schedule = db.relationship('ExamSchedule', backref=db.backref('dummy_stickers', lazy=True))

class FoilMark(db.Model):
    """Marks posted against foil/dummy number"""
    __table_args__ = (db.UniqueConstraint('dummy_number', 'course_id', name='_dummy_course_uc'),)
    id           = db.Column(db.Integer, primary_key=True)
    foil_number  = db.Column(db.String(50), nullable=False)
    dummy_number = db.Column(db.String(50), nullable=False)
    course_id    = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    marks        = db.Column(db.Float)
    practical    = db.Column(db.Float)
    grade        = db.Column(db.String(5))

    course = db.relationship('Course', backref=db.backref('foil_marks', lazy=True))
