import pyodbc
import os

def get_table_name(dsn_name):
    # Connect to the DSN
    conn_str = f"DSN={dsn_name};"
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    
    file_name = None
    try:
        db_path = conn.getinfo(pyodbc.SQL_DATABASE_NAME)
        if db_path:
            file_name = os.path.basename(db_path)
    except Exception:
        pass

    # Get the first table name
    tables = cursor.tables().fetchall()
    
    sheet_name = None
    for table in tables:
        name = table.table_name
        if name.endswith('$') or name.endswith("$'") or name.endswith("$`"):
            sheet_name = name
            break
            
    if not sheet_name:
        sheet_name = tables[0].table_name
        
    conn.close()
    return sheet_name.strip("'").strip("`"), file_name
