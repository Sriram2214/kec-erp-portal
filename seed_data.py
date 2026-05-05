import sqlite3
import datetime

db_path = 'instance/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Add a course if not exists
cursor.execute("SELECT id FROM course WHERE course_code='GE241203'")
course = cursor.fetchone()
if not course:
    cursor.execute("INSERT INTO course (course_code, course_title, department, credits, semester, regulation) VALUES ('GE241203', 'ENGINEERING PHYSICS', 'CSE', 4, 1, 'R2021')")
    course_id = cursor.lastrowid
else:
    course_id = course[0]
    cursor.execute("UPDATE course SET course_title='ENGINEERING PHYSICS', semester=1 WHERE id=?", (course_id,))

# 2. Add an exam schedule if not exists
today = datetime.date.today().strftime('%Y-%m-%d')
cursor.execute("SELECT id FROM exam_schedule WHERE course_id=? AND exam_date=?", (course_id, today))
schedule = cursor.fetchone()
if not schedule:
    cursor.execute("INSERT INTO exam_schedule (course_id, exam_date, session, venue) VALUES (?, ?, 'FN', 'MAIN-HALL-1')", (course_id, today))
    schedule_id = cursor.lastrowid
else:
    schedule_id = schedule[0]

# 3. Add some students for this semester if not exists
cursor.execute("SELECT COUNT(*) FROM student WHERE semester=1")
if cursor.fetchone()[0] == 0:
    students = [
        ('911221104001', 'ABISHEK M', 'CSE', '2021-2025', 1),
        ('911221104002', 'AKASH R', 'CSE', '2021-2025', 1),
        ('911221104003', 'BALAJI S', 'CSE', '2021-2025', 1),
        ('911221104004', 'CHANDRU K', 'CSE', '2021-2025', 1),
        ('911221104005', 'DHARANI P', 'CSE', '2021-2025', 1)
    ]
    for reg, name, dept, batch, sem in students:
        cursor.execute("INSERT INTO student (register_number, name, department, batch, academic_year, semester) VALUES (?, ?, ?, ?, 1, ?)", (reg, name, dept, batch, sem))

conn.commit()
conn.close()
print("Data seeded successfully for testing.")
