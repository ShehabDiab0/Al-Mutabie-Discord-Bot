import sqlite3
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty

connection = sqlite3.connect("tasks.db")

# TODO: Insert User into Database
def subscribe_user(new_subscriber: Subscriber):
    cursor = connection.cursor()

    cursor.execute(f'''
                    INSERT INTO Subscribers (global_user_id, guild_id) VALUES  ({new_subscriber.user_id}, {new_subscriber.guild_id})
                   ''')

    connection.commit()
    cursor.close()


# TODO: Insert User Task into Database
def add_task(new_task: Task):
    pass

# TODO: Insert User Penalty into Database
def add_penalty(new_penalty: Penalty):
    pass

# TODO: Insert New Week
def add_week(new_week: Week):
    pass

# TODO: Get User Week Tasks
def get_subscriber_tasks(subscriber: Subscriber) -> list[Task]:
    pass

# TODO: Get User Penalty History
def get_subscriber_penalty_history(subscriber: Subscriber) -> list[Penalty]:
    pass

# this returns old penalty
# TODO: Update User Penalty
def update_subscriber_penalty(new_penalty: Penalty) -> Penalty:
    pass

# this returns old task
# TODO: Update User Tasks
def update_subscriber_tasks(new_task: Task) -> Task:
    pass

# TODO: Change User Default Penalty



# to initialize database
def init_db():
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    # Subscribers Table
    # we can change is_allowed_to_register with settings
    cursor.execute('''CREATE TABLE IF NOT EXISTS Subscribers (
                      subscriber_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      global_user_id VARCHAR(255),
                      guild_id VARCHAR(255),
                      default_penalty_description MEDIUMTEXT,
                      is_activated BOOLEAN DEFAULT 1,
                      is_allowed_to_register BOOLEAN DEFAULT 0
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
    cursor.close()