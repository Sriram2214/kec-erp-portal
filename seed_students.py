import datetime
from app import create_app, db
from app.models import Course, ExamSchedule, Student, Attendance, DummySticker

def seed():
    app = create_app()
    with app.app_context():
        # Get course id for GE241203
        course = Course.query.filter_by(course_code='GE241203').first()
        if not course:
            print("Course GE241203 not found! Run seed_data.py first.")
            return
        
        course_id = course.id
        semester = course.semester or 1

        # Get or create exam schedule
        today = datetime.date.today()
        schedule = ExamSchedule.query.filter_by(course_id=course_id).first()
        if not schedule:
            schedule = ExamSchedule()
            schedule.course_id = course_id
            schedule.exam_date = today
            schedule.session = 'FN'
            db.session.add(schedule)
            db.session.flush()
        
        schedule_id = schedule.id

        # Realistic KCE student names
        student_data = [
            ('911221104001', 'ABISHEK M', 'CSE'),
            ('911221104002', 'AKASH KUMAR R', 'CSE'),
            ('911221104003', 'ANAND KRISHNA S', 'CSE'),
            ('911221104004', 'ARAVIND KUMAR B', 'CSE'),
            ('911221104005', 'ASHWIN PRASAD K', 'CSE'),
            ('911221104006', 'BALAJI SRINIVASAN V', 'CSE'),
            ('911221104007', 'BHARATH KUMAR S', 'CSE'),
            ('911221104008', 'CHANDRU MOHAN K', 'CSE'),
            ('911221104009', 'DHANUSH KUMAR R', 'CSE'),
            ('911221104010', 'DHARANI DHARAN P', 'CSE'),
            ('911221104011', 'DINESH KUMAR M', 'CSE'),
            ('911221104012', 'GANESH BABU S', 'CSE'),
            ('911221104013', 'GOKUL KRISHNAN R', 'CSE'),
            ('911221104014', 'HARI PRASATH V', 'CSE'),
            ('911221104015', 'HARISH RAGAV K', 'CSE'),
            ('911221104016', 'JAGANATHAN S', 'CSE'),
            ('911221104017', 'JAYASURYA M', 'CSE'),
            ('911221104018', 'KARTHICK RAJA P', 'CSE'),
            ('911221104019', 'KARTHIKEYAN S', 'CSE'),
            ('911221104020', 'KISHORE KUMAR R', 'CSE'),
            ('911221104021', 'LOGESH WARAN B', 'CSE'),
            ('911221104022', 'MANIKANDAN S', 'CSE'),
            ('911221104023', 'MOHAN RAJ V', 'CSE'),
            ('911221104024', 'MUKESH KUMAR R', 'CSE'),
            ('911221104025', 'NAVEEN KUMAR P', 'CSE'),
            ('911221104026', 'NITHISH KUMAR S', 'CSE'),
            ('911221104027', 'PRABHU DEVA M', 'CSE'),
            ('911221104028', 'PRAKASH RAJ K', 'CSE'),
            ('911221104029', 'PRANAV KUMAR S', 'CSE'),
            ('911221104030', 'PRAVEEN KUMAR R', 'CSE'),
            ('911221104031', 'RAGUL KRISHNA V', 'CSE'),
            ('911221104032', 'RAJESH KUMAR B', 'CSE'),
            ('911221104033', 'RANJITH KUMAR S', 'CSE'),
            ('911221104034', 'SAKTHI VEL M', 'CSE'),
            ('911221104035', 'SANDEEP KUMAR R', 'CSE'),
            ('911221104036', 'SANJAY KRISHNA P', 'CSE'),
            ('911221104037', 'SARAVANAN K', 'CSE'),
            ('911221104038', 'SATHISH KUMAR V', 'CSE'),
            ('911221104039', 'SELVAKUMAR S', 'CSE'),
            ('911221104040', 'SIVA PRAKASH M', 'CSE'),
            ('911221104041', 'SRIRAM SUNDAR R', 'CSE'),
            ('911221104042', 'SURESH BABU K', 'CSE'),
            ('911221104043', 'SURYA NARAYANAN P', 'CSE'),
            ('911221104044', 'TAMILSELVAN S', 'CSE'),
            ('911221104045', 'THARUN KUMAR V', 'CSE'),
            ('911221104046', 'THIRUMOORTHY M', 'CSE'),
            ('911221104047', 'VENKATESAN R', 'CSE'),
            ('911221104048', 'VIJAY ANAND K', 'CSE'),
            ('911221104049', 'VIKRAM ADITYA S', 'CSE'),
            ('911221104050', 'VINOTH KUMAR P', 'CSE'),
            ('911221104051', 'VISHNU PRIYA R', 'CSE'),
            ('911221104052', 'YUVARAJ KUMAR S', 'CSE'),
            ('911221104053', 'AJITH KUMAR M', 'CSE'),
            ('911221104054', 'DEEPAK RAJ V', 'CSE'),
            ('911221104055', 'GOWTHAM KUMAR K', 'CSE'),
            ('911221104056', 'JEEVA PRAKASH S', 'CSE'),
            ('911221104057', 'KAVIN KUMAR R', 'CSE'),
            ('911221104058', 'LOKESH BABU P', 'CSE'),
            ('911221104059', 'MADHAN KUMAR S', 'CSE'),
            ('911221104060', 'NIRANJAN KUMAR V', 'CSE'),
            ('911221104061', 'PARTHIBAN M', 'CSE'),
            ('911221104062', 'RAMKUMAR S', 'CSE'),
            ('911221104063', 'SHANMUGAM K', 'CSE'),
            ('911221104064', 'UDHAYAKUMAR R', 'CSE'),
            ('911221104065', 'VASANTH KUMAR P', 'CSE'),
        ]

        # Cleanup
        s_ids = [s.id for s in Student.query.filter_by(semester=semester).all()]
        DummySticker.query.filter(DummySticker.student_id.in_(s_ids)).delete(synchronize_session=False)
        Attendance.query.filter(Attendance.student_id.in_(s_ids)).delete(synchronize_session=False)
        Student.query.filter_by(semester=semester).delete()
        db.session.commit()

        added = 0
        for reg, name, dept in student_data:
            s = Student()
            s.register_number = reg
            s.name = name
            s.department = dept
            s.batch = '2021-2025'
            s.academic_year = 1
            s.semester = semester
            s.degree = 'BE'
            s.regulation = 'R2021'
            db.session.add(s)
            added += 1

        db.session.commit()
        print(f"Done! Added {added} students for Semester {semester} using SQLAlchemy.")

if __name__ == '__main__':
    seed()
