from database import connection
from models.task import Task
from models.subscriber import Subscriber
from data_access import weeks_access

# Insert User Task into Database
def add_task(new_task: Task):
    cursor = connection.cursor()

    cursor.execute(f'''
                    INSERT INTO Tasks (description, week_number, global_user_id, guild_id) VALUES  (?, ?, ?, ?)
                   ''', (new_task.description, new_task.week_number, new_task.owner_id, new_task.guild_id))

    connection.commit()
    cursor.close()


def delete_task(task_id: int):
    cursor = connection.cursor()
    print("TASK ID Inside", task_id)
    cursor.execute(f'''
                    DELETE FROM Tasks WHERE task_id = ?
                   ''', (task_id,))
    connection.commit()
    cursor.close()


def update_task_desc(old_task_id: str, new_task_description):
    cursor = connection.cursor()
    cursor.execute(f'''
                    UPDATE Tasks SET description = ? WHERE task_id = ?
                     ''', (new_task_description, old_task_id))
    connection.commit()

def update_task_completion_percentage(task_id: int, completion_percentage: float):
    cursor = connection.cursor()
    cursor.execute(f'''
                    UPDATE Tasks SET completion_percentage = ? WHERE task_id = ?
                     ''', (completion_percentage, task_id))
    connection.commit()


# Get User Week Tasks (week_number = 0 means current week)
def get_subscriber_tasks(subscriber: Subscriber, week_number: int) -> list[Task]:
    current_week = weeks_access.get_current_week()
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


def get_subscriber_first_week(subscriber: Subscriber) -> int:
    cursor = connection.cursor()
    cursor.execute(f'''
                    SELECT week_number
                    FROM Tasks
                    WHERE global_user_id = ? AND guild_id = ?
                    ORDER BY week_number ASC LIMIT 1
                ''', (subscriber.user_id, subscriber.guild_id))
    output = cursor.fetchone()
    connection.commit()
    cursor.close()
    if output:
        return output[0]
    return -1