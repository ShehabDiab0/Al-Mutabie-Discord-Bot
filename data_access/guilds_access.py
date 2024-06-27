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