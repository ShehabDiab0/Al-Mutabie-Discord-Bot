from database import connection
from models.subscriber import Subscriber
from models.penalty import Penalty
# TODO: replace SELECT (*) with column names

def get_subscriber_penalty_history(subscriber: Subscriber) -> list[Penalty]:
    cursor = connection.cursor()
    cursor.execute(f"""
                    SELECT penalty_id, description, is_done, is_yellow, week_number
                    FROM Penalties
                    WHERE global_user_id = ? AND guild_id = ?
                    """, (subscriber.user_id, subscriber.guild_id))
    output = cursor.fetchall()
    penalties = []
    for penalty in output:
        penalties.append(Penalty(penalty_id=penalty[0], description=penalty[1], is_done=penalty[2], is_yellow=penalty[3], week_number=penalty[4], guild_id=subscriber.guild_id, owner_id=subscriber.user_id))
    connection.commit()
    cursor.close()
    if penalties:
        return penalties
    return []


def add_penalty(penalty: Penalty) -> None:
    cursor = connection.cursor()
    cursor.execute(f'''
                    INSERT INTO Penalties (description, is_done, is_yellow, week_number, global_user_id, guild_id) VALUES  (?, ?, ?, ?, ?, ?)
                ''', (penalty.description, 0, penalty.is_yellow, penalty.week_number, penalty.owner_id, penalty.guild_id))

    connection.commit()
    cursor.close()


def update_subscriber_penalty(new_penalty: Penalty) -> None:
    cursor = connection.cursor()
    cursor.execute(f"""
                    UPDATE Penalties
                    SET is_done = ?
                    WHERE penalty_id = ?
                    """, (new_penalty.is_done, new_penalty.penalty_id))
    connection.commit()
    cursor.close()

def get_penalty(user_id: str, guild_id: str) -> Penalty:
    cursor =connection.cursor()
    cursor.execute(f"""
                    SELECT penalty_id, description, is_done, is_yellow, week_number
                    FROM Penalties
                    WHERE global_user_id = ? AND guild_id = ?
                    ORDER BY week_number DESC LIMIT 1
                    """, (user_id, guild_id))
    # get latest penalty
    penalty = cursor.fetchone()
    connection.commit()
    cursor.close()
    if penalty:
        return Penalty(penalty_id=penalty[0], description=penalty[1], is_done=penalty[2], is_yellow=penalty[3], week_number=penalty[4], guild_id=guild_id, owner_id=user_id)
    return None


def get_penalties_for_week(week_number: int, guild_id: str) -> list[Penalty]:
    cursor = connection.cursor()
    cursor.execute(f"""
                    SELECT penalty_id, description, is_done, is_yellow, week_number, global_user_id
                    FROM Penalties
                    WHERE week_number = ? AND guild_id = ?
                    """, (week_number, guild_id))
    output = cursor.fetchall()
    penalties = []
    for penalty in output:
        penalties.append(Penalty(penalty_id=penalty[0], description=penalty[1], is_done=penalty[2], is_yellow=penalty[3], week_number=penalty[4], guild_id=guild_id, owner_id=penalty[5]))
    connection.commit()
    cursor.close()
    return penalties