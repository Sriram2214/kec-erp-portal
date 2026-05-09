from app import create_app, db
from app.models import Course, Student, CourseRegistration, ExamSchedule, DummySticker
import datetime as dt, random, string
app = create_app()
with app.app_context():
    course_id = 1600
    schedule = ExamSchedule.query.filter_by(course_id=course_id).first()
    students = (db.session.query(Student)
                .join(CourseRegistration, CourseRegistration.student_id == Student.id)
                .filter(CourseRegistration.course_id == course_id).all())
                
    stickers = {ds.student_id for ds in DummySticker.query.filter_by(exam_schedule_id=schedule.id).all()}
    to_gen = [s for s in students if s.id not in stickers]
    
    print(f'Need to generate {len(to_gen)} stickers...')
    if to_gen:
        year_prefix = str(dt.datetime.now().year % 100)
        used = {d[0] for d in db.session.query(DummySticker.dummy_number).filter(DummySticker.dummy_number.like(f"{year_prefix}%")).all()}
        new_s = []
        for s in to_gen:
            dept_p = "".join(filter(str.isalnum, (s.department or 'GEN')))[:3].upper()
            while True:
                rand = ''.join(random.choices(string.digits, k=5))
                dno = f"{year_prefix}{dept_p}{rand}"
                if dno not in used:
                    used.add(dno)
                    break
            new_s.append(DummySticker(student_id=s.id, exam_schedule_id=schedule.id, dummy_number=dno, foil_number=str(random.randint(10000, 99999))))
        db.session.bulk_save_objects(new_s)
        db.session.commit()
        print(f'Successfully generated {len(new_s)} stickers.')
    else:
        print('All stickers already exist.')
