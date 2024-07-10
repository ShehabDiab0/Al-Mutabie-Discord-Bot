import caribou
import sqlite3
import sys

# Config
db_url = sys.argv[1] if len(sys.argv) >= 2 else "tasks.db"
migrations_dir = './migrations/'

# Auto apply migrations
caribou.upgrade(db_url, migrations_dir)

# Connect to database
connection = sqlite3.connect(db_url, check_same_thread=False)
connection.execute("PRAGMA foreign_keys = ON")

# to initialize database
def init_db():
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")


    # Guilds settings table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Guilds (
                      guild_id VARCHAR(255) PRIMARY KEY,
                      reminder_channel_id VARCHAR(255),
                      allow_kicks BOOL DEFAULT 0,
                      reminder_day INTEGER DEFAULT 0,
                      offset_days INTEGER DEFAULT 2
                    )''')
    
    # Subscribers Table
    # we can change is_banned with settings
    cursor.execute('''CREATE TABLE IF NOT EXISTS Subscribers (
                      global_user_id VARCHAR(255),
                      guild_id VARCHAR(255),
                      default_red_penalty_description MEDIUMTEXT,
                      default_yellow_penalty_description MEDIUMTEXT,
                      threshold FLOAT DEFAULT 0.60,
                      is_banned BOOLEAN DEFAULT 0,
                      PRIMARY KEY (global_user_id, guild_id),
                      FOREIGN KEY (guild_id) REFERENCES Guilds(guild_id) ON DELETE CASCADE
                    )''')
    
    # Weeks Table 
    cursor.execute('''CREATE TABLE IF NOT EXISTS Weeks (
                      week_number INTEGER PRIMARY KEY AUTOINCREMENT,
                      start_date DATETIME,
                      end_date DATETIME
                    )''')
    
    # Tasks Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Tasks (
                      task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      description MEDIUMTEXT,
                      completion_percentage FLOAT DEFAULT 0.0,
                      week_number INTEGER,
                      global_user_id VARCHAR(255),
                      guild_id VARCHAR(255),
                      FOREIGN KEY (week_number) REFERENCES Weeks(week_number),
                      FOREIGN KEY (global_user_id, guild_id) REFERENCES Subscribers(global_user_id, guild_id)
                    )''')
    
    # Penalties Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Penalties (
                      penalty_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      description MEDIUMTEXT,
                      is_done BOOLEAN DEFAULT 0,
                      is_yellow BOOLEAN DEFAULT 1,
                      week_number INTEGER,
                      global_user_id VARCHAR(255),
                      guild_id VARCHAR(255),
                      FOREIGN KEY (week_number) REFERENCES Weeks(week_number),
                      FOREIGN KEY (global_user_id, guild_id) REFERENCES Subscribers(global_user_id, guild_id)
                    )''')
    
    connection.commit()
    def verify_init():
        res = cursor.execute("SELECT name FROM sqlite_master")
        tables = res.fetchall()
        print("Tables in the database:", tables)

    verify_init()
    cursor.close()
