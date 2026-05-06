import random
from app import create_app, db
from app.models import Student

app = create_app()

def feed_data():
    with app.app_context():
        print('Wiping existing students...')
        Student.query.delete()
        db.session.commit()
        
        depts = ['AI&DS', 'AIML', 'BME', 'CSE', 'ECE', 'IT', 'MECH', 'CIVIL', 'RAA']
        batches = ['2021-2025', '2022-2026', '2023-2027', '2024-2028']
        
        first_names = ['Arun', 'Balaji', 'Karthik', 'Siva', 'Manoj', 'Vijay', 'Ajith', 'Surya', 'Vikram', 'Dhanush', 'Sriram', 'Naveen', 'Praveen', 'Gokul', 'Sanjay', 'Rahul', 'Vignesh', 'Hari', 'Prasanth', 'Mohan', 'Kavya', 'Priya', 'Shruthi', 'Sneha', 'Swathi', 'Divya', 'Ramya', 'Nithya', 'Preethi', 'Ananya', 'Nandhini', 'Meena', 'Aarthi', 'Gowri']
        last_names = ['Kumar', 'Raj', 'Kannan', 'Krishnan', 'Prakash', 'Chandran', 'Murugan', 'Vel', 'Nathan', 'Iyer', 'Reddy', 'G', 'S', 'V', 'K', 'M', 'R', 'A', 'N', 'P']
        
        students = []
        count = 0
        for dept in depts:
            for b_idx, batch in enumerate(batches):
                year = 4 - b_idx
                sem = year * 2
                
                # 55 students per batch per dept = 1980 students total
                for i in range(1, 56):
                    count += 1
                    year_prefix = batch[2:4] # 21, 22, 23, 24
                    dept_code = dept[:2].upper() if dept != 'AI&DS' else 'AD'
                    if dept == 'CIVIL': dept_code = 'CE'
                    if dept == 'MECH': dept_code = 'ME'
                    reg_no = f'{year_prefix}1{dept_code}{i:03d}'
                    
                    name = f'{random.choice(first_names)} {random.choice(last_names)}'
                    email = f'{name.lower().replace(" ", ".")}@{batch[:4]}.kec.ac.in'
                    phone = f'9{random.randint(100000000, 999999999)}'
                    
                    s = Student(
                        register_number=reg_no,
                        name=name,
                        department=dept,
                        batch=batch,
                        academic_year=year,
                        semester=sem,
                        degree='B.E',
                        regulation='R2021',
                        email=email,
                        phone=phone,
                        result_published=False
                    )
                    students.append(s)
        
        db.session.bulk_save_objects(students)
        db.session.commit()
        print(f'Successfully fed {len(students)} realistic students!')

if __name__ == '__main__':
    feed_data()
