from database import connection
from models.subscriber import Subscriber


def subscribe_user(new_subscriber: Subscriber):
    cursor = connection.cursor()

    cursor.execute(f'''
                    INSERT 
                    INTO 
                    Subscribers 
                    (global_user_id, guild_id, default_yellow_penalty_description, default_red_penalty_description, threshold)
                    VALUES (?, ?, ?, ?, ?)
                   ''', (new_subscriber.user_id,
                         new_subscriber.guild_id,
                         new_subscriber.default_yellow_description,
                         new_subscriber.default_red_description,
                         new_subscriber.threshold_percentage))

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