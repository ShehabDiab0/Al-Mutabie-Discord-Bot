from models.task import Task
from models.subscriber import Subscriber
from client import bot
import re

def convert_tasks_to_str(tasks: list[Task]) -> str:
    if len(tasks) == 0:
        return "Empty! متخازل"
    
    formatted_tasks = ''
    for i, task in enumerate(tasks):
        formatted_tasks += f'{i + 1}- {task.description} - [{task.completion_percentage}]\n'

    return formatted_tasks

def convert_tasks_to_self_report(tasks: list[Task]) -> str:
    if len(tasks) == 0:
        return "Empty! متخازل"
      
    formatted_tasks = ''
    for i, task in enumerate(tasks):
        formatted_tasks += f'{i + 1}- {task.description} - []\n'
    
    return formatted_tasks

def convert_subscriber_profile_to_str(subscriber: Subscriber):
    return  f'''Name: {bot.get_user(int(subscriber.user_id)).display_name}
                Default Yellow Card: {subscriber.default_yellow_description}
                Default Red Card: {subscriber.default_red_description}
                Default Completion Threshold: {subscriber.threshold_percentage}
                Banned: {"YES!!!" if subscriber.is_banned else "no :^)" }
            '''

def convert_formatted_tasks_to_percentages(formatted_tasks: str) -> list[float]:
    tasks = []
    tasks_str = formatted_tasks.split("\n")
    pattern = r'\[(.*?)\]'
    completion_percentages = re.findall(pattern, formatted_tasks)
    return completion_percentages


def is_float(num: str) -> bool:
    try:
        str(num)
        return True
    except ValueError:
        return False