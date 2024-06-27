from database import connection
from models.subscriber import Subscriber
from models.penalty import Penalty

def get_subscriber_penalty_history(subscriber: Subscriber) -> list[Penalty]:
    cursor = connection.cursor()
    cursor.execute(f'''
                    SELECT penalty_id, description, is_done, is_yellow, week_number
                    FROM Penalties
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

# TODO: Insert User Penalty into Database
def add_penalty(new_penalty: Penalty):
    pass

# TODO: Update User Penalty
def update_subscriber_penalty(new_penalty: Penalty) -> Penalty:
    pass