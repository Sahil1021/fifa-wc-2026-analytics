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

def create_schema():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Teams table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='teams' AND xtype='U')
    CREATE TABLE teams (
        team_id INT PRIMARY KEY IDENTITY(1,1),
        team_name NVARCHAR(100) NOT NULL,
        fifa_code NVARCHAR(3),
        confederation NVARCHAR(20),
        group_name NVARCHAR(2),
        fifa_ranking INT,
        created_at DATETIME DEFAULT GETDATE()
    )
    """)
    print("✅ Teams table created")

    # Matches table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='matches' AND xtype='U')
    CREATE TABLE matches (
        match_id INT PRIMARY KEY IDENTITY(1,1),
        match_date DATETIME,
        stage NVARCHAR(50),
        group_name NVARCHAR(2),
        home_team_id INT FOREIGN KEY REFERENCES teams(team_id),
        away_team_id INT FOREIGN KEY REFERENCES teams(team_id),
        home_score INT,
        away_score INT,
        venue NVARCHAR(100),
        city NVARCHAR(100),
        attendance INT,
        created_at DATETIME DEFAULT GETDATE()
    )
    """)
    print("✅ Matches table created")

    # Players table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='players' AND xtype='U')
    CREATE TABLE players (
        player_id INT PRIMARY KEY IDENTITY(1,1),
        player_name NVARCHAR(100) NOT NULL,
        team_id INT FOREIGN KEY REFERENCES teams(team_id),
        position NVARCHAR(20),
        age INT,
        caps INT,
        goals INT,
        created_at DATETIME DEFAULT GETDATE()
    )
    """)
    print("✅ Players table created")

    # Match events table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='match_events' AND xtype='U')
    CREATE TABLE match_events (
        event_id INT PRIMARY KEY IDENTITY(1,1),
        match_id INT FOREIGN KEY REFERENCES matches(match_id),
        player_id INT FOREIGN KEY REFERENCES players(player_id),
        event_type NVARCHAR(50),
        event_minute INT,
        created_at DATETIME DEFAULT GETDATE()
    )
    """)
    print("✅ Match events table created")

    # Group standings table
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='group_standings' AND xtype='U')
    CREATE TABLE group_standings (
        standing_id INT PRIMARY KEY IDENTITY(1,1),
        team_id INT FOREIGN KEY REFERENCES teams(team_id),
        group_name NVARCHAR(2),
        played INT DEFAULT 0,
        won INT DEFAULT 0,
        drawn INT DEFAULT 0,
        lost INT DEFAULT 0,
        goals_for INT DEFAULT 0,
        goals_against INT DEFAULT 0,
        goal_difference INT DEFAULT 0,
        points INT DEFAULT 0,
        updated_at DATETIME DEFAULT GETDATE()
    )
    """)
    print("✅ Group standings table created")

    conn.commit()
    conn.close()
    print("\n🎉 All tables created successfully in Azure SQL!")

if __name__ == "__main__":
    create_schema()