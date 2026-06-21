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
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='predictions' AND xtype='U')
CREATE TABLE predictions (
    prediction_id INT PRIMARY KEY IDENTITY(1,1),
    team_name NVARCHAR(100) NOT NULL,
    group_name NVARCHAR(10),
    played INT,
    points INT,
    goal_difference INT,
    goals_for INT,
    goals_per_game FLOAT,
    fifa_ranking INT,
    momentum_score FLOAT,
    advancement_prob FLOAT,
    advancement_prob_pct FLOAT,
    win_probability FLOAT,
    updated_at DATETIME DEFAULT GETDATE()
)
""")

conn.commit()
conn.close()
print("✅ Predictions table created!")