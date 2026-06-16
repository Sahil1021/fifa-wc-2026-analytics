import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')},1433;"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)

def fix_schema():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fix teams table
    cursor.execute("ALTER TABLE teams ALTER COLUMN confederation NVARCHAR(100)")
    print("✅ Fixed confederation column")
    
    cursor.execute("ALTER TABLE teams ALTER COLUMN team_name NVARCHAR(200)")
    print("✅ Fixed team_name column")

    # Fix matches table
    cursor.execute("ALTER TABLE matches ALTER COLUMN group_name NVARCHAR(20)")
    print("✅ Fixed matches group_name column")

    cursor.execute("ALTER TABLE matches ALTER COLUMN stage NVARCHAR(100)")
    print("✅ Fixed matches stage column")

    cursor.execute("ALTER TABLE matches ALTER COLUMN venue NVARCHAR(200)")
    print("✅ Fixed matches venue column")

    cursor.execute("ALTER TABLE matches ALTER COLUMN city NVARCHAR(200)")
    print("✅ Fixed matches city column")

    # Fix group_standings table
    cursor.execute("ALTER TABLE group_standings ALTER COLUMN group_name NVARCHAR(20)")
    print("✅ Fixed group_standings group_name column")

    conn.commit()
    conn.close()
    print("\n🎉 All columns fixed!")

if __name__ == "__main__":
    fix_schema()