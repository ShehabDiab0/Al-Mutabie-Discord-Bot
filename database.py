import sqlite3
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
import schedule
import datetime
import time

# modal

connection = sqlite3.connect("tasks.db", check_same_thread=False)

# TODO: Insert User into Database
def subscribe_user(new_subscriber: Subscriber):
    cursor = connection.cursor()

    cursor.execute(f'''
                    INSERT INTO Subscribers (global_user_id, guild_id) VALUES  (?, ?)
                   ''', (new_subscriber.user_id, new_subscriber.guild_id))

    connection.commit()
    cursor.close()


def is_banned_user(user_id: str, guild_id: str) -> bool:
    cursor = connection.cursor()
    cursor.execute(f'''SELECT is_banned 
                    From 
                    Subscribers 
                    WHERE global_user_id = ? AND guild_id = ?''',
                    (user_id, guild_id))
    is_banned = cursor.fetchone()
    connection.commit()
    cursor.close()

    if is_banned:
        return is_banned[0]
    return None

def is_registered_user(user_id: str, guild_id: str) -> bool:
    cursor = connection.cursor()
    cursor.execute(f'''SELECT 1
                    From 
                    Subscribers 
                    WHERE global_user_id = ? AND guild_id = ?''',
                    (user_id, guild_id))
    is_registered = cursor.fetchone()
    connection.commit()
    cursor.close()

    if is_registered is None:
        return False
    return True


# TODO: Insert User Task into Database
def add_task(new_task: Task):
    cursor = connection.cursor()

    cursor.execute(f'''
                    INSERT INTO Tasks (description, week_number, global_user_id, guild_id) VALUES  (?, ?, ?, ?)
                   ''', (new_task.description, new_task.week_number, new_task.owner_id, new_task.guild_id))

    connection.commit()
    cursor.close()

# TODO: Insert User Penalty into Database
def add_penalty(new_penalty: Penalty):
    pass

# TODO: Insert New Week
@schedule.repeat(schedule.every().thursday.at('21:00'))
def add_week():
    print("INSERTED A NEW ONE HEHE")
    cursor = connection.cursor()

    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(weeks=1)

    cursor.execute(f'''
                    INSERT INTO Weeks (start_date, end_date) VALUES  (?, ?)
                   ''', (start_date, end_date))

    connection.commit()
    cursor.close()

def get_current_week():
    cursor = connection.cursor()
    cursor.execute(f'''
                    SELECT week_number FROM Weeks ORDER BY week_number DESC LIMIT 1
                   ''')
    current_week = cursor.fetchone()
    connection.commit()
    cursor.close()

    if current_week:
        return current_week[0]
    return None

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
    # we can change is_banned with settings
    cursor.execute('''CREATE TABLE IF NOT EXISTS Subscribers (
                      global_user_id VARCHAR(255),
                      guild_id VARCHAR(255),
                      default_penalty_description MEDIUMTEXT,
                      is_banned BOOLEAN DEFAULT 0,
                      PRIMARY KEY (global_user_id, guild_id)
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