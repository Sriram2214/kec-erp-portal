import sqlite3
import os

db_path = 'instance/app.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for row in cursor.fetchall():
    print(f"- {row[0]}")

print("\nCourses (GE241203):")
cursor.execute("SELECT course_code, course_title, semester FROM course WHERE course_code='GE241203'")
print(cursor.fetchall())

print("\nStudent Counts by Semester:")
cursor.execute("SELECT semester, COUNT(*) FROM student GROUP BY semester")
print(cursor.fetchall())

conn.close()
