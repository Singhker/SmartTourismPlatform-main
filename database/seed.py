import os
import sys
import sqlite3

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.import_csv import import_all_datasets, get_db_connection

def init_database(db_path='database/tourism_platform.db'):
    """Initialize the database with schema and data."""
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if os.path.exists(schema_path):
        conn = get_db_connection(db_path)
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()
        print("✅ Database schema created successfully")
    else:
        print(f"⚠️ Schema file not found: {schema_path}")
        return False
    
    # Import data from CSV files
    datasets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets')
    import_all_datasets(datasets_dir, db_path)
    
    print("\n✅ Database initialization complete!")
    return True

if __name__ == '__main__':
    init_database()