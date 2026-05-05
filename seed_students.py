import sqlite3
import datetime

db_path = 'instance/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get course id for GE241203
cursor.execute("SELECT id, semester FROM course WHERE course_code='GE241203'")
course_row = cursor.fetchone()
if not course_row:
    print("Course GE241203 not found!")
    exit(1)
course_id = course_row[0]
semester = course_row[1] or 1

# Get or create exam schedule
today = datetime.date.today().strftime('%Y-%m-%d')
cursor.execute("SELECT id FROM exam_schedule WHERE course_id=?", (course_id,))
sched = cursor.fetchone()
if not sched:
    cursor.execute("INSERT INTO exam_schedule (course_id, exam_date, session) VALUES (?, ?, 'FN')", (course_id, today))
    schedule_id = cursor.lastrowid
else:
    schedule_id = sched[0]

# Realistic KCE student names (Tamil Nadu style)
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

# Delete old test students for this semester and re-insert
cursor.execute("DELETE FROM dummy_sticker WHERE student_id IN (SELECT id FROM student WHERE semester=?)", (semester,))
cursor.execute("DELETE FROM attendance WHERE student_id IN (SELECT id FROM student WHERE semester=?)", (semester,))
cursor.execute("DELETE FROM student WHERE semester=?", (semester,))

added = 0
for reg, name, dept in student_data:
    cursor.execute(
        "INSERT INTO student (register_number, name, department, batch, academic_year, semester, degree, regulation) VALUES (?, ?, ?, '2021-2025', 1, ?, 'BE', 'R2021')",
        (reg, name, dept, semester)
    )
    added += 1

conn.commit()
conn.close()
print(f"Done! Added {added} students for Semester {semester}.")
