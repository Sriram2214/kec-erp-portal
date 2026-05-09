from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint

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

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

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

    def __init__(self, **kwargs):
        super(Degree, self).__init__(**kwargs)

class Department(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    code      = db.Column(db.String(10), unique=True, nullable=False)   # CSE, ECE …
    name      = db.Column(db.String(100), nullable=False)
    degree_id = db.Column(db.Integer, db.ForeignKey('degree.id'), nullable=False)

    def __init__(self, **kwargs):
        super(Department, self).__init__(**kwargs)

class Regulation(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)  # R2021, R2019 …

    def __init__(self, **kwargs):
        super(Regulation, self).__init__(**kwargs)

class AcademicYear(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    label      = db.Column(db.String(20), unique=True, nullable=False) # 2023-24, 2024-25
    semester   = db.Column(db.String(10), nullable=False)              # ODD / EVEN
    is_current = db.Column(db.Boolean, default=False)
    
    # Visibility Controls
    hall_ticket_published = db.Column(db.Boolean, default=False)
    results_published     = db.Column(db.Boolean, default=False)

    def __repr__(self): return f'<AY {self.label} {self.semester}>'

    def __init__(self, **kwargs):
        super(AcademicYear, self).__init__(**kwargs)

class Batch(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), unique=True, nullable=False)  # 2021-2025

    def __init__(self, **kwargs):
        super(Batch, self).__init__(**kwargs)

# ─────────────────────────────────────────────
# Students & Faculty
# ─────────────────────────────────────────────
class Student(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.String(20), unique=True, nullable=False)
    name            = db.Column(db.String(100), nullable=False)
    department      = db.Column(db.String(50), index=True, nullable=False)   # dept code
    batch           = db.Column(db.String(20), index=True, nullable=False)
    academic_year   = db.Column(db.Integer, index=True, nullable=False)      # 1 / 2 / 3 / 4
    degree          = db.Column(db.String(20), default='BE')
    regulation      = db.Column(db.String(20), default='R2021')
    semester        = db.Column(db.Integer, index=True, default=1)
    email           = db.Column(db.String(120))
    phone           = db.Column(db.String(15))
    dob             = db.Column(db.String(12))
    result_published = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)

class Faculty(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    department  = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(80))
    email       = db.Column(db.String(120))
    phone       = db.Column(db.String(15))

    def __init__(self, **kwargs):
        super(Faculty, self).__init__(**kwargs)

# ─────────────────────────────────────────────
# Courses & Curriculum
# ─────────────────────────────────────────────
class Curriculum(db.Model):
    """Master mapping for Batch + Dept + Regulation"""
    id            = db.Column(db.Integer, primary_key=True)
    degree_id     = db.Column(db.Integer, db.ForeignKey('degree.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    batch_id      = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    regulation_id = db.Column(db.Integer, db.ForeignKey('regulation.id'), nullable=False)

    degree     = db.relationship('Degree', backref='curriculums')
    department = db.relationship('Department', backref='curriculums')
    batch      = db.relationship('Batch', backref='curriculums')
    regulation = db.relationship('Regulation', backref='curriculums')

    courses    = db.relationship('Course', backref='curriculum', cascade='all, delete-orphan')

    __table_args__ = (db.UniqueConstraint('degree_id', 'department_id', 'batch_id', 'regulation_id', name='_curriculum_mapping_uc'),)

    def __init__(self, **kwargs):
        super(Curriculum, self).__init__(**kwargs)

class Course(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    curriculum_id = db.Column(db.Integer, db.ForeignKey('curriculum.id'), nullable=False)
    course_code   = db.Column(db.String(20), index=True, nullable=False)
    course_title  = db.Column(db.String(150), nullable=False)
    semester      = db.Column(db.Integer, nullable=False)
    credits       = db.Column(db.Integer, default=3)
    is_lab        = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint('curriculum_id', 'course_code', name='_curriculum_course_uc'),)

    def __init__(self, **kwargs):
        super(Course, self).__init__(**kwargs)

class CourseAllocation(db.Model):
    """Faculty ↔ Course mapping per section"""
    id               = db.Column(db.Integer, primary_key=True)
    faculty_id       = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    section          = db.Column(db.String(5), default='A')
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))

    faculty       = db.relationship('Faculty', backref=db.backref('allocations', lazy=True))
    course        = db.relationship('Course',  backref=db.backref('allocations', lazy=True))
    academic_year = db.relationship('AcademicYear')

    def __init__(self, **kwargs):
        super(CourseAllocation, self).__init__(**kwargs)

class GradeScale(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    grade      = db.Column(db.String(5), nullable=False) # O, A+, A, B+...
    min_mark   = db.Column(db.Integer, nullable=False)
    max_mark   = db.Column(db.Integer, nullable=False)
    points     = db.Column(db.Integer, nullable=False)
    
    def __init__(self, **kwargs):
        super(GradeScale, self).__init__(**kwargs)

class ClassTimetable(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    allocation_id = db.Column(db.Integer, db.ForeignKey('course_allocation.id'), nullable=False)
    day_of_week   = db.Column(db.String(10), nullable=False) # Monday, Tuesday...
    period        = db.Column(db.Integer, nullable=False)      # 1, 2, 3, 4, 5, 6, 7, 8
    
    allocation    = db.relationship('CourseAllocation', backref=db.backref('periods', lazy=True))

    def __init__(self, **kwargs):
        super(ClassTimetable, self).__init__(**kwargs)

# ─────────────────────────────────────────────
# Attendance
# ─────────────────────────────────────────────
class ClassAttendance(db.Model):
    """Day-wise class attendance entry"""
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), index=True, nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), index=True, nullable=False)
    date             = db.Column(db.Date, index=True, nullable=False)
    session          = db.Column(db.String(5), default='FN')   # FN / AN
    status           = db.Column(db.String(10), default='P')   # P / A / OD
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))

    student      = db.relationship('Student', backref=db.backref('class_attendance', lazy=True))
    course       = db.relationship('Course',  backref=db.backref('class_attendance', lazy=True))

    def __init__(self, **kwargs):
        super(ClassAttendance, self).__init__(**kwargs)

# ─────────────────────────────────────────────
# Internal Marks
# ─────────────────────────────────────────────
class InternalMarks(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), index=True, nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), index=True, nullable=False)
    ia1              = db.Column(db.Float, default=0)
    ia2              = db.Column(db.Float, default=0)
    ia3              = db.Column(db.Float, default=0)
    assignment_marks = db.Column(db.Float, default=0)
    marks            = db.Column(db.Float, default=0)   # computed best of 2
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))

    student = db.relationship('Student', backref=db.backref('internal_marks', lazy=True))
    course  = db.relationship('Course',  backref=db.backref('internal_marks', lazy=True))

    def __init__(self, **kwargs):
        super(InternalMarks, self).__init__(**kwargs)

# ─────────────────────────────────────────────
# End Semester Exam
# ─────────────────────────────────────────────
class ExamSchedule(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), index=True, nullable=False)
    exam_date        = db.Column(db.Date, index=True, nullable=False)
    session          = db.Column(db.String(5), nullable=False)   # FN / AN
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))
    venue            = db.Column(db.String(50))

    course       = db.relationship('Course', backref=db.backref('schedules', lazy=True))
    academic_year = db.relationship('AcademicYear')

    def __init__(self, **kwargs):
        super(ExamSchedule, self).__init__(**kwargs)

class CourseRegistration(db.Model):
    """Student-wise course registration — current + backlogs"""
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), index=True, nullable=False)
    course_id        = db.Column(db.Integer, db.ForeignKey('course.id'), index=True, nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))
    is_backlog       = db.Column(db.Boolean, default=False)
    registered_on    = db.Column(db.DateTime, default=datetime.utcnow)

    student      = db.relationship('Student', backref=db.backref('registrations', lazy=True))
    course       = db.relationship('Course',  backref=db.backref('registrations', lazy=True))

    def __init__(self, **kwargs):
        super(CourseRegistration, self).__init__(**kwargs)

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

    def __init__(self, **kwargs):
        super(FeeClearance, self).__init__(**kwargs)

class HallTicket(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'))
    generated_at     = db.Column(db.DateTime, default=datetime.utcnow)
    generated_by     = db.Column(db.String(64))

    student = db.relationship('Student', backref=db.backref('hall_tickets', lazy=True))

    def __init__(self, **kwargs):
        super(HallTicket, self).__init__(**kwargs)



class Attendance(db.Model):
    """ESE Exam attendance"""
    __table_args__ = (UniqueConstraint('student_id', 'exam_schedule_id', name='_student_exam_uc'),)
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), index=True, nullable=False)
    exam_schedule_id = db.Column(db.Integer, db.ForeignKey('exam_schedule.id'), index=True, nullable=False)
    status           = db.Column(db.String(20), index=True, default='Present')  # Present / Absent / Malpractice

    student      = db.relationship('Student',      backref=db.backref('attendances', lazy=True))
    exam_schedule = db.relationship('ExamSchedule', backref=db.backref('attendances', lazy=True))

    def __init__(self, **kwargs):
        super(Attendance, self).__init__(**kwargs)

# ─────────────────────────────────────────────
# Semester-Level Dummy Allocation (COE Architecture)
# One dummy number per student per semester — used across ALL courses that semester
# ─────────────────────────────────────────────
class SemesterDummyAllocation(db.Model):
    """One dummy number per student per semester per academic year.
    Used consistently across all exam reports (Attendance, Cover Sheet, Stickers, Despatch)."""
    __tablename__ = 'semester_dummy_allocation'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'semester', 'academic_year_id', name='_student_sem_ay_dummy_uc'),
    )
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), index=True, nullable=False)
    semester         = db.Column(db.Integer, nullable=False)           # 1–8
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_year.id'), nullable=False)
    dummy_number     = db.Column(db.String(50), unique=True, nullable=False, index=True)
    foil_number      = db.Column(db.String(50))
    allocated_on     = db.Column(db.DateTime, default=datetime.utcnow)

    student      = db.relationship('Student',      backref=db.backref('dummy_allocations', lazy=True))
    academic_year = db.relationship('AcademicYear', backref=db.backref('dummy_allocations', lazy=True))

    def __init__(self, **kwargs):
        super(SemesterDummyAllocation, self).__init__(**kwargs)


class DummySticker(db.Model):
    """Per-exam-schedule sticker — links to SemesterDummyAllocation for the dummy number."""
    __table_args__ = (db.UniqueConstraint('student_id', 'exam_schedule_id', name='_stu_exam_dummy_uc'),)
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('student.id'), index=True, nullable=False)
    exam_schedule_id = db.Column(db.Integer, db.ForeignKey('exam_schedule.id'), index=True, nullable=False)
    # Resolved from SemesterDummyAllocation — stored for fast PDF rendering
    dummy_number     = db.Column(db.String(50), index=True, nullable=False)
    foil_number      = db.Column(db.String(50), nullable=False)

    student       = db.relationship('Student',      backref=db.backref('dummy_stickers', lazy=True))
    exam_schedule = db.relationship('ExamSchedule', backref=db.backref('dummy_stickers', lazy=True))

    def __init__(self, **kwargs):
        super(DummySticker, self).__init__(**kwargs)

class FoilMark(db.Model):
    """Marks posted against foil/dummy number"""
    __table_args__ = (db.UniqueConstraint('dummy_number', 'course_id', name='_dummy_course_uc'),)
    id           = db.Column(db.Integer, primary_key=True)
    foil_number  = db.Column(db.String(50), index=True, nullable=False)
    dummy_number = db.Column(db.String(50), index=True, nullable=False)
    course_id    = db.Column(db.Integer, db.ForeignKey('course.id'), index=True, nullable=False)
    marks        = db.Column(db.Float)
    practical    = db.Column(db.Float)
    grade        = db.Column(db.String(5))

    course = db.relationship('Course', backref=db.backref('foil_marks', lazy=True))

    def __init__(self, **kwargs):
        super(FoilMark, self).__init__(**kwargs)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100)) # e.g. "MARK_ENTRY", "LOGIN_FAIL"
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(AuditLog, self).__init__(**kwargs)

class SystemIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    severity = db.Column(db.String(20), default='info') # info, warning, critical
    category = db.Column(db.String(50)) # DB, API, AUTH
    message = db.Column(db.Text)
    traceback = db.Column(db.Text, nullable=True)
    is_resolved = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(SystemIssue, self).__init__(**kwargs)
