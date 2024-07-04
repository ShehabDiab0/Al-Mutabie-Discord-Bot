from models.task import Task
from models.subscriber import Subscriber
import discord
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
    return  f'''Default Yellow Card 🟨:\n {subscriber.default_yellow_description}\n                   
                Default Red Card 🟥:\n {subscriber.default_red_description}\n                     
                Default Completion Threshold: {subscriber.threshold_percentage}
                Banned : {"🅱️" if subscriber.is_banned else "🟩" }
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


def is_valid_number(input_str):
    # allows integer or float from 0 to 100
    pattern = r"^(100|(\d{1,2})(\.\d+)?|0(\.\d+)?)$"
    match = re.match(pattern, input_str)
    return bool(match)

def is_valid_discord_mention(mention: str) -> bool:
    pattern = r'^<@!?(\d+)>$'
    return bool(re.match(pattern, mention))

async def is_existing_discord_user(user_id: str) -> bool:
    try:
        user = await bot.fetch_user(user_id)
        return user is not None
    except Exception as e:
        print(e)
        return False