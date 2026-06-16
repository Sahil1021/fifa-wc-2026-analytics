import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_connection():
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server},1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    
    conn = pyodbc.connect(connection_string)
    return conn

# Test connection
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Connected to Azure SQL Database successfully!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")