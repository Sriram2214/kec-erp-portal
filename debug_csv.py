import pandas as pd
df = pd.read_csv('original_student_details.csv')
print("Total rows:", len(df))
print("Null counts:\n", df.isnull().sum())
print("Duplicate Register Numbers:", df['REGISTER NO'].duplicated().sum())
if df['REGISTER NO'].duplicated().any():
    print(df[df['REGISTER NO'].duplicated(keep=False)].sort_values('REGISTER NO').head(10))
