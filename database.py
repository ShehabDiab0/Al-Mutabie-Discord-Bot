import sqlite3
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
import client
import datetime




connection = sqlite3.connect("tasks.db", check_same_thread=False)
############################# INSERTION FUNCTIONS #############################
# TODO: Insert User into Database
def subscribe_user(new_subscriber: Subscriber):
    cursor = connection.cursor()

    cursor.execute(f'''
                    INSERT INTO Subscribers (global_user_id, guild_id) VALUES  (?, ?)
                   ''', (new_subscriber.user_id, new_subscriber.guild_id))

    connection.commit()
    cursor.close()

# Insert User Task into Database
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

# Insert New Week
def add_week():
    print("INSERTED A NEW ONE HEHE")
    cursor = connection.cursor()

    start_date = datetime.datetime.now()
    start_date = client.TIMEZONE.localize(start_date)
    
    # get the days ahead to reach the next Thursday
    days_ahead = (3 - start_date.weekday() + 7) % 7
    end_date = start_date + datetime.timedelta(days=days_ahead)
    end_date = end_date.replace(hour=23, minute=59, second=59)

    cursor.execute(f'''
                    INSERT INTO Weeks (start_date, end_date) VALUES  (?, ?)
                   ''', (start_date, end_date))

    connection.commit()
    cursor.close()

############################# DELETION FUNCTIONS  #############################
def delete_task(task_id: int):
    cursor = connection.cursor()
    print("TASK ID Inside", task_id)
    cursor.execute(f'''
                    DELETE FROM Tasks WHERE task_id = ?
                   ''', (task_id,))
    connection.commit()
    cursor.close()
############################# UPDATE FUNCTIONS    #############################

# this returns old penalty
# TODO: Update User Penalty
def update_subscriber_penalty(new_penalty: Penalty) -> Penalty:
    pass

# this returns old task
# TODO: Update User Tasks
def update_subscriber_task(old_task_id: str, new_task_description):
    cursor = connection.cursor()
    cursor.execute(f'''
                    UPDATE Tasks SET description = ? WHERE task_id = ?
                     ''', (new_task_description, old_task_id))
    connection.commit()

############################# SELECT FUNCTIONS    #############################

# Get User Week Tasks (week_number = 0 means current week)
def get_subscriber_tasks(subscriber: Subscriber, week_number: int) -> list[Task]:
    current_week = get_current_week()
    if(week_number == 0):
        week_number = current_week

    if week_number > current_week or week_number < 0:
        return []
    cursor = connection.cursor()
    cursor.execute(f'''
                    SELECT task_id, description, completion_percentage
                    FROM Tasks
                    WHERE week_number = ? AND global_user_id = ? AND guild_id = ?
                   ''', (week_number, subscriber.user_id, subscriber.guild_id))
    output = cursor.fetchall()
    tasks = []
    for task in output:
        tasks.append(Task(task_id=task[0], description=task[1], completion_percentage=task[2], week_number=week_number, guild_id=subscriber.guild_id, owner_id=subscriber.user_id))
    connection.commit()
    cursor.close()
    if tasks:
        return tasks
    return []

# Get User Penalty History
def get_subscriber_penalty_history(subscriber: Subscriber) -> list[Penalty]:
    cursor = connection.cursor()
    cursor.execute(f'''
                    SELECT penalty_id, description, is_done, is_yellow, week_number
                    FROM Tasks
                    WHERE global_user_id = ? AND guild_id = ?)
                     ''', (subscriber.user_id, subscriber.guild_id))
    output = cursor.fetchall()
    penalties = []
    for penalty in output:
        penalties.append(Penalty(penalty_id=penalty[0], description=penalty[1], is_done=penalty[2], is_yellow=penalty[3], week_number=penalty[4], guild_id=subscriber.guild_id, owner_id=subscriber.user_id))
    connection.commit()
    cursor.close()
    if penalties:
        return penalties
    return []

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

def get_current_week_start_end():
    cursor = connection.cursor()
    cursor.execute(f'''
                    SELECT start_date, end_date FROM Weeks ORDER BY week_number DESC LIMIT 1
                   ''')
    current_week = cursor.fetchone()
    connection.commit()
    cursor.close()

    if current_week:
        return current_week
    return None

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
    return False # if user is not registered, he is not banned

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
############################# DATABASE INITIALIZATION ##########################

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