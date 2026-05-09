import pandas as pd

file_path = 'COURSE DETAIL - 2021 TO 2025.xlsx'
try:
    xl = pd.ExcelFile(file_path)
    print("Sheets found:", xl.sheet_names)
    
    sheet_name = 'Course Detail'
    if sheet_name in xl.sheet_names:
        print(f"Reading sheet: {sheet_name}")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        csv_name = 'original_course_details.csv'
        df.to_csv(csv_name, index=False)
        print(f"Saved {len(df)} courses to {csv_name}")
        print("Columns:", df.columns.tolist())
    else:
        print(f"Sheet '{sheet_name}' not found.")

except Exception as e:
    print(f"Error: {e}")
