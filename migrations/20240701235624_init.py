def upgrade(connection):
    connection.executescript('''
        -- Guilds settings table
        CREATE TABLE IF NOT EXISTS Guilds (
            guild_id VARCHAR(255) PRIMARY KEY,
            reminder_channel_id VARCHAR(255),
            allow_kicks BOOL DEFAULT 0,
            reminder_day INTEGER DEFAULT 0,
            offset_days INTEGER DEFAULT 2
        );

        -- Subscribers Table
        CREATE TABLE IF NOT EXISTS Subscribers (
            global_user_id VARCHAR(255),
            guild_id VARCHAR(255),
            default_red_penalty_description MEDIUMTEXT,
            default_yellow_penalty_description MEDIUMTEXT,
            threshold FLOAT DEFAULT 0.6,
            is_banned BOOLEAN DEFAULT 0,
            PRIMARY KEY (global_user_id, guild_id),
            FOREIGN KEY (guild_id) REFERENCES Guilds(guild_id)
        );

        -- Weeks Table
        CREATE TABLE IF NOT EXISTS Weeks (
            week_number INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date DATETIME,
            end_date DATETIME
        );

        -- Tasks Table
        CREATE TABLE IF NOT EXISTS Tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            description MEDIUMTEXT,
            completion_percentage FLOAT DEFAULT 0.0,
            week_number INTEGER,
            global_user_id VARCHAR(255),
            guild_id VARCHAR(255),
            FOREIGN KEY (week_number) REFERENCES Weeks(week_number),
            FOREIGN KEY (global_user_id, guild_id) REFERENCES Subscribers(global_user_id, guild_id)
        );

        -- Penalties Table
        CREATE TABLE IF NOT EXISTS Penalties (
            penalty_id INTEGER PRIMARY KEY AUTOINCREMENT,
            description MEDIUMTEXT,
            is_done BOOLEAN DEFAULT 0,
            is_yellow BOOLEAN DEFAULT 1,
            week_number INTEGER,
            global_user_id VARCHAR(255),
            guild_id VARCHAR(255),
            FOREIGN KEY (week_number) REFERENCES Weeks(week_number),
            FOREIGN KEY (global_user_id, guild_id) REFERENCES Subscribers(global_user_id, guild_id)
        );
    ''')
    connection.commit()

def downgrade(connection):
    connection.executescript('''
        DROP TABLE IF EXISTS Guilds;
        DROP TABLE IF EXISTS Subscribers;
        DROP TABLE IF EXISTS Weeks;
        DROP TABLE IF EXISTS Tasks;
        DROP TABLE IF EXISTS Penalties;
    ''')
    connection.commit()
