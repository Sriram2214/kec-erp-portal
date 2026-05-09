import pandas as pd

file_path = 'COURSE DETAIL - 2021 TO 2025.xlsx'
try:
    xl = pd.ExcelFile(file_path)
    print("Sheets found:", xl.sheet_names)
    
    # Try to read the first sheet or look for a 'Student' sheet
    target_sheet = xl.sheet_names[0]
    for sheet in xl.sheet_names:
        if 'student' in sheet.lower():
            target_sheet = sheet
            break
            
    print(f"Reading sheet: {target_sheet}")
    df = pd.read_excel(file_path, sheet_name=target_sheet)
    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Save to CSV
    csv_name = 'original_student_details.csv'
    df.to_csv(csv_name, index=False)
    print(f"\nSaved to {csv_name}")

except Exception as e:
    print(f"Error: {e}")
