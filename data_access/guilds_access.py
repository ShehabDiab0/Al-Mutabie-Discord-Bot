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