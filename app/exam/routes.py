from flask import render_template, request, jsonify
from flask_login import login_required
from app import db
from app.exam import exam_bp
from app.models import ExamSchedule, Attendance, Student

@exam_bp.route('/')
@login_required
def exam_dashboard():
    schedules = ExamSchedule.query.all()
    return render_template('exam/dashboard.html', title='Exam Management', schedules=schedules)

@exam_bp.route('/attendance/<int:schedule_id>')
@login_required
def mark_attendance(schedule_id):
    schedule = ExamSchedule.query.get_or_404(schedule_id)
    
    # In a real app, you'd filter students enrolled in this course for this batch
    # For demonstration, we'll fetch all students
    students = Student.query.all()
    
    # Fetch existing attendance records
    attendances = Attendance.query.filter_by(exam_schedule_id=schedule_id).all()
    attendance_dict = {a.student_id: a.status for a in attendances}
    
    return render_template('exam/attendance.html', 
                           title=f'Attendance: {schedule.course.course_code}', 
                           schedule=schedule, 
                           students=students,
                           attendance_dict=attendance_dict)

@exam_bp.route('/api/attendance/update', methods=['POST'])
@login_required
def update_attendance():
    data = request.json
    student_id = data.get('student_id')
    schedule_id = data.get('schedule_id')
    status = data.get('status')
    
    attendance = Attendance.query.filter_by(
        student_id=student_id, 
        exam_schedule_id=schedule_id
    ).first()
    
    if attendance:
        attendance.status = status
    else:
        attendance = Attendance(student_id=student_id, exam_schedule_id=schedule_id, status=status)
        db.session.add(attendance)
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Attendance updated'})

from flask import make_response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io

@exam_bp.route('/despatch/<int:schedule_id>')
@login_required
def generate_despatch(schedule_id):
    schedule = ExamSchedule.query.get_or_404(schedule_id)
    
    # Get students marked as Present (or default Present if no record exists)
    # First, get all students (in a real app, only enrolled ones)
    students = Student.query.all()
    attendances = Attendance.query.filter_by(exam_schedule_id=schedule_id).all()
    attendance_dict = {a.student_id: a.status for a in attendances}
    
    present_students = []
    for student in students:
        status = attendance_dict.get(student.id, 'Present')
        if status == 'Present':
            present_students.append(student)
            
    # Generate PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    def draw_header(c, page_num):
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2.0, height - 50, "KINGS ENGINEERING COLLEGE")
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2.0, height - 70, "EXAMINATION DESPATCH REPORT")
        
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 100, f"Course: {schedule.course.course_code} - {schedule.course.course_title}")
        c.drawString(width - 200, height - 100, f"Date: {schedule.exam_date.strftime('%d-%m-%Y')}")
        c.drawString(width - 200, height - 115, f"Session: {schedule.session}")
        
        # Table Header
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 140, "S.No")
        c.drawString(100, height - 140, "Register Number")
        c.drawString(250, height - 140, "Student Name")
        c.drawString(450, height - 140, "Department")
        c.line(40, height - 145, width - 40, height - 145)

    # Pagination logic (max 30 per page)
    max_per_page = 30
    page_num = 1
    y_position = height - 165
    
    draw_header(c, page_num)
    c.setFont("Helvetica", 10)
    
    for i, student in enumerate(present_students):
        if i > 0 and i % max_per_page == 0:
            c.showPage()
            page_num += 1
            draw_header(c, page_num)
            y_position = height - 165
            c.setFont("Helvetica", 10)
            
        c.drawString(50, y_position, str(i + 1))
        c.drawString(100, y_position, student.register_number)
        c.drawString(250, y_position, student.name)
        c.drawString(450, y_position, student.department)
        y_position -= 20
        
    c.save()
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=despatch_{schedule.course.course_code}.pdf'
    return response

@exam_bp.route('/stickers/<int:schedule_id>')
@login_required
def generate_stickers(schedule_id):
    schedule = ExamSchedule.query.get_or_404(schedule_id)
    
    # In a full app, this would use the uploaded excel sheet to map foil numbers.
    # Here we mock the dummy number generation for present students.
    students = Student.query.all()
    attendances = Attendance.query.filter_by(exam_schedule_id=schedule_id).all()
    attendance_dict = {a.student_id: a.status for a in attendances}
    
    present_students = []
    for student in students:
        status = attendance_dict.get(student.id, 'Present')
        if status == 'Present':
            present_students.append(student)

    # Generate PDF (3x4 Grid)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # A4 is approx 595 x 842 points
    # 3 columns, 4 rows
    cols = 3
    rows = 4
    stickers_per_page = cols * rows
    sticker_width = width / cols
    sticker_height = height / rows
    
    for i, student in enumerate(present_students):
        if i > 0 and i % stickers_per_page == 0:
            c.showPage()
            
        # Calculate position
        pos_in_page = i % stickers_per_page
        col = pos_in_page % cols
        row = pos_in_page // cols
        
        x = col * sticker_width
        y = height - ((row + 1) * sticker_height)
        
        # Draw sticker border (optional, good for printing)
        c.setStrokeColor(colors.lightgrey)
        c.rect(x + 10, y + 10, sticker_width - 20, sticker_height - 20)
        
        # Dummy number (mocked here, should come from DummySticker table)
        dummy_no = f"{schedule.course.course_code}-{student.register_number[-4:]}"
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 20, y + sticker_height - 40, "KEC EXAMINATION")
        c.setFont("Helvetica", 10)
        c.drawString(x + 20, y + sticker_height - 65, f"Date: {schedule.exam_date.strftime('%d-%m-%Y')}")
        c.drawString(x + 20, y + sticker_height - 85, f"Session: {schedule.session}")
        c.drawString(x + 20, y + sticker_height - 105, f"Course: {schedule.course.course_code}")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 20, y + 40, f"Dummy No: {dummy_no}")
        
    c.save()
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=stickers_{schedule.course.course_code}.pdf'
    return response


import pandas as pd
from flask import flash, redirect, url_for
from app.models import DummySticker

@exam_bp.route('/upload_dummy/<int:schedule_id>', methods=['POST'])
@login_required
def upload_dummy(schedule_id):
    schedule = ExamSchedule.query.get_or_404(schedule_id)
    
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('exam.exam_dashboard'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('exam.exam_dashboard'))
        
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Expected columns: Register Number, Dummy Number, Foil Number
            required_cols = ['Register Number', 'Dummy Number', 'Foil Number']
            if not all(col in df.columns for col in required_cols):
                flash('Missing required columns. Expected: Register Number, Dummy Number, Foil Number', 'error')
                return redirect(url_for('exam.exam_dashboard'))
                
            success_count = 0
            # Process dataframe
            for _, row in df.iterrows():
                reg_no = str(row['Register Number']).strip()
                dummy_no = str(row['Dummy Number']).strip()
                foil_no = str(row['Foil Number']).strip()
                
                student = Student.query.filter_by(register_number=reg_no).first()
                if student:
                    # Check if exists
                    existing = DummySticker.query.filter_by(
                        student_id=student.id, 
                        exam_schedule_id=schedule_id
                    ).first()
                    
                    if existing:
                        existing.dummy_number = dummy_no
                        existing.foil_number = foil_no
                    else:
                        new_sticker = DummySticker(
                            student_id=student.id,
                            exam_schedule_id=schedule_id,
                            dummy_number=dummy_no,
                            foil_number=foil_no
                        )
                        db.session.add(new_sticker)
                    success_count += 1
            
            db.session.commit()
            flash(f'Successfully mapped {success_count} dummy numbers.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing file: {str(e)}', 'error')
            
    else:
        flash('Invalid file type. Please upload a CSV or Excel file.', 'error')
        
    return redirect(url_for('exam.exam_dashboard'))

from app.models import InternalMarks, Course

@exam_bp.route('/marks/<int:course_id>', methods=['GET', 'POST'])
@login_required
def marks_entry(course_id):
    course = Course.query.get_or_404(course_id)
    students = Student.query.all()
    
    if request.method == 'POST':
        for student in students:
            marks = request.form.get(f'marks_{student.id}')
            assignment = request.form.get(f'assignment_{student.id}')
            
            if marks or assignment:
                record = InternalMarks.query.filter_by(student_id=student.id, course_id=course_id).first()
                if not record:
                    record = InternalMarks(student_id=student.id, course_id=course_id)
                    db.session.add(record)
                
                if marks:
                    record.marks = float(marks)
                if assignment:
                    record.assignment_marks = float(assignment)
                    
        db.session.commit()
        flash('Marks saved successfully', 'success')
        return redirect(url_for('exam.marks_entry', course_id=course_id))
        
    existing_marks = InternalMarks.query.filter_by(course_id=course_id).all()
    marks_dict = {m.student_id: m for m in existing_marks}
    
    return render_template('exam/marks_entry.html', title=f'Marks Entry: {course.course_code}', course=course, students=students, marks_dict=marks_dict)
