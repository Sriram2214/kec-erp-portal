import json
from app import create_app, db
from sqlalchemy import inspect, text

def backup_to_sql():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        backup_file = 'kec_erp_pre_original_import.sql'
        print(f"Starting backup to {backup_file}...")
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("-- KCE ERP Production Backup\n")
            f.write(f"-- Generated on: {app.config.get('SUPABASE_URL', 'Local')}\n\n")
            
            for table in tables:
                print(f"Backing up table: {table}")
                f.write(f"-- Data for table: {table}\n")
                
                # Fetch all rows
                result = db.session.execute(text(f"SELECT * FROM {table}"))
                columns = result.keys()
                rows = result.fetchall()
                
                for row in rows:
                    vals = []
                    for v in row:
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, str):
                            safe_v = v.replace("'", "''")
                            vals.append(f"'{safe_v}'")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        else:
                            vals.append(f"'{v}'")
                    
                    col_names = ", ".join(columns)
                    val_str = ", ".join(vals)
                    f.write(f"INSERT INTO {table} ({col_names}) VALUES ({val_str});\n")
                f.write("\n")
                
        print("Backup completed successfully.")

if __name__ == "__main__":
    backup_to_sql()
