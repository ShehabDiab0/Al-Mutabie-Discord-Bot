import sqlite3

connection = sqlite3.connect("tasks.db")
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

def init_db():
    # Subscribers Table
    # we can change is_allowed_to_register with settings
    cursor.execute('''CREATE TABLE IF NOT EXISTS Subscribers (
                      subscriber_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      global_user_id VARCHAR(255),
                      guild_id VARCHAR(255),
                      is_activated BOOLEAN DEFAULT 0,
                      is_allowed_to_register BOOLEAN DEFAULT 1
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
                      subscriber_id INTEGER,
                      FOREIGN KEY (week_number) REFERENCES Weeks(week_number),
                      FOREIGN KEY (subscriber_id) REFERENCES Subscribers(subscriber_id)
                    )''')
    
    # Penalties Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Penalties (
                      penalty_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      description MEDIUMTEXT,
                      is_done BOOLEAN DEFAULT 0,
                      is_yellow BOOLEAN DEFAULT 1,
                      week_number INTEGER,
                      subscriber_id INTEGER,
                      FOREIGN KEY (week_number) REFERENCES Weeks(week_number),
                      FOREIGN KEY (subscriber_id) REFERENCES Subscribers(subscriber_id)
                    )''')
    
    connection.commit()
    def verify_init():
        res = cursor.execute("SELECT name FROM sqlite_master")
        tables = res.fetchall()
        print("Tables in the database:", tables)

    verify_init()


# TODO: Insert User into Database
def insert_user():
    pass


# TODO: Insert User Task into Database

# TODO: Insert User Penalty into Database

# TODO: Get User Week Tasks

# TODO: Get User Penalty History

# TODO: Update User Penalty

# TODO: Update User Tasks

# TODO: Change User Default Penalty