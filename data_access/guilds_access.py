from database import connection
from models.guild import Guild


def add_guild(new_guild: Guild):
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO Guilds (guild_id, reminder_channel_id, allow_kicks, reminder_day, offset_days)
        VALUES (?, ?, ?, ?, ?)
    ''', (new_guild.guild_id, new_guild.reminder_channel_id, new_guild.allow_kicks, new_guild.reminder_day, new_guild.offset_days))
    connection.commit()
    cursor.close()

def update_guild_reminder_channel(guild_id, new_channel_id: str):
    cursor = connection.cursor()

    cursor.execute('''
        UPDATE Guilds 
        SET reminder_channel_id = ?
        WHERE guild_id = ?
    ''', (new_channel_id, guild_id,))
    connection.commit()
    cursor.close()

def is_registered_guild(guild_id: str) -> bool:
    cursor = connection.cursor()
    cursor.execute(f'''SELECT 1
                    From 
                    Guilds 
                    WHERE guild_id = ?''',
                    (guild_id,))
    is_registered = cursor.fetchone()
    connection.commit()
    cursor.close()
    if is_registered is None:
        return False
    return True


def get_channel_id(guild_id: str) -> str:
    cursor = connection.cursor()
    cursor.execute(f'''SELECT reminder_channel_id
                    From 
                    Guilds 
                    WHERE guild_id = ?''',
                    (guild_id,))
    channel_id = cursor.fetchone()
    connection.commit()
    cursor.close()
    return channel_id[0]


def get_today_guilds(day: int) -> list[Guild]:
    cursor = connection.cursor()
    cursor.execute(f'''SELECT guild_id, reminder_channel_id, allow_kicks, reminder_day, offset_days
                    FROM Guilds
                    WHERE (reminder_day + offset_days) % 7 = ?''',
                    (day,))
    # This query is for testing purposes
    # cursor.execute('''SELECT guild_id, reminder_channel_id, allow_kicks, reminder_day, offset_days
    #                 FROM Guilds
    #                 ''')
    output = cursor.fetchall()
    # parse each guild in the list
    apply = []
    for guild in output:
        apply.append(Guild(guild[0], guild[1], guild[2], guild[3], guild[4]))
    cursor.execute(f'''SELECT guild_id, reminder_channel_id, allow_kicks, reminder_day, offset_days
                    FROM Guilds
                    WHERE reminder_day % 7 = ?''',
                    (day,))
    # This query is for testing purposes
    # cursor.execute('''SELECT guild_id, reminder_channel_id, allow_kicks, reminder_day, offset_days
    #                 FROM Guilds
    #                 ''')
    output = cursor.fetchall()
    reminder = []
    for guild in output:
        reminder.append(Guild(guild[0], guild[1], guild[2], guild[3], guild[4]))
    connection.commit()
    cursor.close()
    return reminder, apply