from database import connection
from models.subscriber import Subscriber

# TODO: replace SELECT (*) with column names

def subscribe_user(new_subscriber: Subscriber):
    cursor = connection.cursor()

    cursor.execute(f'''
                    INSERT 
                    INTO 
                    Subscribers 
                    (global_user_id, guild_id, default_yellow_penalty_description, default_red_penalty_description, threshold, strict_mode)
                    VALUES (?, ?, ?, ?, ?, ?)
                   ''', (new_subscriber.user_id,
                         new_subscriber.guild_id,
                         new_subscriber.default_yellow_description,
                         new_subscriber.default_red_description,
                         new_subscriber.threshold_percentage,
                         1 if new_subscriber.strict_mode else 0))

    connection.commit()
    cursor.close()

def get_subscriber(user_id, guild_id) -> Subscriber:
    cursor = connection.cursor()
    cursor.execute(f'''SELECT *
                    From 
                    Subscribers
                    WHERE global_user_id = ? AND guild_id = ?''',
                    (user_id, guild_id))
    subscriber_data = cursor.fetchone()
    connection.commit()
    cursor.close()

    subscriber = Subscriber(user_id=subscriber_data[0],
               guild_id=subscriber_data[1],
               default_red_description=subscriber_data[2],
               default_yellow_description=subscriber_data[3],
               threshold_percentage=subscriber_data[4],
               is_banned=subscriber_data[5],
               strict_mode=(True if subscriber_data[6] == 1 else False),
               color_mode=subscriber[7])
    return subscriber


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

def get_subscribers(guild_id: str) -> list[Subscriber]:
    cursor = connection.cursor()
    # print(guild_id)
    cursor.execute('''
                    SELECT *
                    FROM Subscribers
                    WHERE is_banned = 0 AND guild_id = ?''', (guild_id,))
    output = cursor.fetchall()
    subscribers = []
    for subscriber in output:
        subscribers.append(Subscriber(user_id=subscriber[0],
                                      guild_id=subscriber[1],
                                      default_red_description=subscriber[2],
                                      default_yellow_description=subscriber[3],
                                      threshold_percentage=subscriber[4],
                                      is_banned=subscriber[5],
                                      strict_mode=(True if subscriber[6] == 1 else False),
                                      color_mode=subscriber[7]))
    connection.commit()
    cursor.close()
    return subscribers


# TODO: ban user test
def ban_user(subscriber: Subscriber) -> None:
    cursor = connection.cursor()
    cursor.execute(f'''
                    UPDATE Subscribers
                    SET is_banned = 1
                    WHERE global_user_id = ? AND guild_id = ?
                    ''', (subscriber.user_id, subscriber.guild_id))
    connection.commit()
    cursor.close()


def update_subscriber_threshold(user_id: str, guild_id: str, new_threshold: float):
    cursor = connection.cursor()
    cursor.execute(f'''
                    UPDATE Subscribers
                    SET threshold = ?
                    WHERE global_user_id = ? AND guild_id = ?
                    ''', (new_threshold, user_id, guild_id))
    connection.commit()
    cursor.close()

def update_subscriber_yellow_card(user_id: str, guild_id: str, yellow_description: str):
    cursor = connection.cursor()
    cursor.execute(f'''
                    UPDATE Subscribers
                    SET default_yellow_penalty_description = ?
                    WHERE global_user_id = ? AND guild_id = ?
                    ''', (yellow_description, user_id, guild_id))
    connection.commit()
    cursor.close()

def update_subscriber_red_card(user_id: str, guild_id: str, yellow_description: str):
    cursor = connection.cursor()
    cursor.execute(f'''
                    UPDATE Subscribers
                    SET default_red_penalty_description = ?
                    WHERE global_user_id = ? AND guild_id = ?
                    ''', (yellow_description, user_id, guild_id))
    connection.commit()
    cursor.close()

def update_ban_status(user_id: str, guild_id: str, is_banned: bool):
    cursor = connection.cursor()
    cursor.execute(f'''
                    UPDATE Subscribers
                    SET is_banned = ?
                    WHERE global_user_id = ? AND guild_id = ?
                    ''', (is_banned, user_id, guild_id))
    connection.commit()
    cursor.close()

def update_strict_mode(user_id: str, guild_id: str, activate: bool):
    cursor = connection.cursor()
    cursor.execute(f'''
                        UPDATE Subscribers
                        SET strict_mode = ?
                        WHERE global_user_id = ? AND guild_id = ?
                        ''', (1 if activate else 0, user_id, guild_id))
    connection.commit()
    cursor.close()

def update_color_mode(user_id: str, guild_id: str, color_mode: str):
    cursor = connection.cursor()
    cursor.execute(f'''
                        UPDATE Subscribers
                        SET color_mode = ?
                        WHERE global_user_id = ? AND guild_id = ?
                        ''', (color_mode, user_id, guild_id))
    connection.commit()
    cursor.close()

def get_subscriber_color_mode(user_id, guild_id) -> Subscriber:
    cursor = connection.cursor()
    cursor.execute(f'''SELECT color_mode
                    From 
                    Subscribers
                    WHERE global_user_id = ? AND guild_id = ?''',
                    (user_id, guild_id))
    subscriber_data = cursor.fetchone()
    connection.commit()
    cursor.close()

    return subscriber_data[0]