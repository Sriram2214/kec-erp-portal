import pandas as pd
from app import create_app, db
from app.models import Student

def import_students():
    app = create_app()
    with app.app_context():
        df = pd.read_csv('original_student_details.csv')
        # Drop duplicates based on REGISTER NO
        df = df.drop_duplicates(subset=['REGISTER NO'])
        print(f"Importing {len(df)} unique students...")
        
        students = []
        for index, row in df.iterrows():
            try:
                reg_no = str(row['REGISTER NO']).strip()
                if not reg_no or reg_no == 'nan': continue
                
                # Derive batch from Register No (e.g. 210821... -> 2021-2025)
                # Some colleges use 5th and 6th digits for year
                # In 210821..., 5-6 digits are '21'
                year_short = reg_no[4:6]
                if not year_short.isdigit():
                    # Fallback to first two digits if that fails
                    year_short = reg_no[:2]
                
                batch_start = f"20{year_short}"
                batch_end = str(int(batch_start) + 4) # Assuming 4 year UG
                batch_label = f"{batch_start}-{batch_end}"
                
                # Basic degree mapping
                degree_branch = str(row['DEGREE & BRANCH'])
                degree = 'BE'
                if 'B.Tech' in degree_branch: degree = 'B.Tech'
                elif 'ME' in degree_branch: degree = 'ME'
                
                # Academic Year calculation (assuming current is 2024-2025)
                # Batch 2021-2025 -> Year 4
                # Batch 2022-2026 -> Year 3
                # Batch 2023-2027 -> Year 2
                # Batch 2024-2028 -> Year 1
                try:
                    start_yr_int = int(batch_start)
                    academic_year = 2025 - start_yr_int
                except:
                    academic_year = 1
                    
                if academic_year < 1: academic_year = 1
                if academic_year > 4: academic_year = 4
                
                s = Student(
                    register_number=reg_no,
                    name=row['NAME OF THE STUDENT'],
                    department=row['DEPT'],
                    batch=batch_label,
                    academic_year=academic_year,
                    degree=degree,
                    regulation=row['REGULATION'],
                    semester=academic_year * 2, # Assuming even semester/end of year
                    dob=row['DOB']
                )
                students.append(s)
                
                if len(students) >= 100:
                    db.session.bulk_save_objects(students)
                    db.session.commit()
                    students = []
                    print(f"Imported {index + 1} students...")

            except Exception as e:
                print(f"Error importing row {index}: {e}")

        if students:
            db.session.bulk_save_objects(students)
            db.session.commit()
            
        print("Import completed successfully!")

if __name__ == "__main__":
    import_students()
