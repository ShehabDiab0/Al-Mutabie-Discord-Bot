import sqlite3

connection = sqlite3.connect("tasks.db")
cursor = connection.cursor()

# TODO: Initialize DB
def init_db():
    # Subscribers Table
    # we can change is_allowed_to_register with settings
    cursor.execute('''CREATE TABLE IF NOT EXISTS Subscribers (
                      subscriber_id INT NOT NULL AUTO_INCREMENT,
                      global_user_id VARCHAR(255),
                      guild_id VARCHAR(255),
                      is_activated BIT DEFAULT 0,
                      is_allowed_to_register BIT DEFAULT 1,
                      PRIMARY KEY(subscriber_id)
                    )''')
    
    # Weeks Table 
    cursor.execute('''CREATE TABLE IF NOT EXISTS Weeks (
                      week_number INT NOT NULL AUTO_INCREMENT,
                      start_date DATETIME,
                      end_date DATETIME,
                      PRIMARY KEY(week_number)
                    )''')
    
    # Tasks Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Tasks (
                      task_id INT NOT NULL AUTO_INCREMENT,
                      description MEDIUMTEXT,
                      completion_percentage FLOAT DEFAULT 0.0,
                      PRIMARY KEY(task_id),
                      week_number INT FOREIGN KEY REFERENCES Weeks(week_number),
                      subscriber_id INT FOREIGN KEY REFERENCES Subscribers(subscriber_id)
                    )''')
    
    # Penalty Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Penalties (
                      penalty_id INT NOT NULL AUTO_INCREMENT,
                      description MEDIUMTEXT,
                      is_done BIT DEFAULT 0,
                      is_yellow BIT DEFAULT 1,
                      PRIMARY KEY(penalty_id),
                      week_number INT FOREIGN KEY REFERENCES Weeks(week_number),
                      subscriber_id INT FOREIGN KEY REFERENCES Subscribers(subscriber_id)
                    )''')



# TODO: Insert User into Database

# TODO: Insert User Task into Database

# TODO: Insert User Penalty into Database

# TODO: Get User Week Tasks

# TODO: Get User Penalty History

# TODO: Update User Penalty

# TODO: Update User Tasks

# TODO: Change User Default Penalty