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

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT team_id, team_name, fifa_code FROM teams WHERE team_name LIKE '%Urug%'")
for row in cursor.fetchall():
    print(row)
conn.close()