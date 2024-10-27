from models.task import Task
from models.subscriber import Subscriber
import discord
from client import bot
from data_access import subscribers_access
import re
import math

def convert_tasks_to_str(tasks: list[Task], color_mode: str = 'dfm') -> str:
    if len(tasks) == 0:
        return "Empty! متخازل"
    
    tasks.sort(key=lambda task: task.completion_percentage)
    if color_mode == 'hlm':
        return get_colored_tasks_hlm(tasks)
    if color_mode == 'fcm':
        return get_colored_tasks_fcm(tasks)
    if color_mode == 'skm':
        return get_colored_tasks_skm(tasks)
    if color_mode == 'ssm':
        return get_colored_tasks_ssm(tasks)
    
    # dfm
    return get_colored_tasks_dfm(tasks)

def get_color_mode_name(color_mode_abbreviation: str) -> str:
    if color_mode_abbreviation == 'hlm':
        return "Highlight Mode"
    if color_mode_abbreviation == 'fcm':
        return "Font Color Mode"
    if color_mode_abbreviation == 'skm':
        return "Strike Mode"
    if color_mode_abbreviation == 'ssm':
        return "Shifted Strike Mode"

# default color mode
def get_colored_tasks_dfm(tasks):
    formatted_tasks = '\n'
    for i, task in enumerate(tasks):
            formatted_tasks += f'{i + 1}- {task.description} - [{task.completion_percentage}]\n'

    total_progress = get_total_progress(tasks)
    formatted_tasks += f'\n`Total Progress: {"💯" if total_progress == 100 else total_progress}`\n'

    return formatted_tasks

# Highlight Color Mode
def get_colored_tasks_hlm(tasks):
    formatted_tasks = '```diff\n'
    for i, task in enumerate(tasks):
        if task.completion_percentage == 100:
            formatted_tasks += f'+ {task.description} ✅\n'
        elif task.completion_percentage == 0:
            formatted_tasks += f'- {i + 1}- {task.description} - [{task.completion_percentage}]\n'
        else:
            formatted_tasks += f'{i + 1}- {task.description} - [{task.completion_percentage}]\n'

    total_progress = get_total_progress(tasks)
    formatted_tasks += f'``` ```Total Progress: {"💯" if total_progress == 100 else total_progress}```\n'

    return formatted_tasks

# Font Color Mode
def get_colored_tasks_fcm(tasks):
    formatted_tasks = '```md\n'
    for i, task in enumerate(tasks):
        if task.completion_percentage == 100:
            formatted_tasks += f'> {task.description} ✅\n'
        elif task.completion_percentage >= 50:
            formatted_tasks += f'# {i + 1}- {task.description} - [{task.completion_percentage}]\n'
        else:
            formatted_tasks += f'{i + 1}- {task.description} - [{task.completion_percentage}]\n'

    total_progress = get_total_progress(tasks)
    formatted_tasks += f'``` ```Total Progress: {"💯" if total_progress == 100 else total_progress}```\n'

    return formatted_tasks

# Strike Color Mode
def get_colored_tasks_skm(tasks):
    formatted_tasks = ''
    for i, task in enumerate(tasks):
        if task.completion_percentage == 100:
            formatted_tasks += f'~~{task.description}~~ ✅\n'
        else:
            formatted_tasks += f'{i + 1}- {task.description} - [{task.completion_percentage}]\n'

    total_progress = get_total_progress(tasks)
    formatted_tasks += f'\n`Total Progress: {"💯" if total_progress == 100 else total_progress}`\n'

    return formatted_tasks

# Shifted Strike Color Mode
def get_colored_tasks_ssm(tasks):
    formatted_tasks = ''
    for i, task in enumerate(tasks):
        if task.completion_percentage == 100:
            formatted_tasks += f'> ~~{task.description}~~ ✅\n'
        else:
            formatted_tasks += f'{i + 1}- {task.description} - [{task.completion_percentage}]\n'

    total_progress = get_total_progress(tasks)
    formatted_tasks += f'\n`Total Progress: {"💯" if total_progress == 100 else total_progress}`\n'

    return formatted_tasks

def get_total_progress(tasks: list[Task]) -> float:
    total_progress: float = 0.0
    for task in tasks:
        total_progress += task.completion_percentage
    if len(tasks) == 0:
        return 0.00
    return round(total_progress/len(tasks), 2)

def convert_tasks_to_self_report(tasks: list[Task]) -> str:
    if len(tasks) == 0:
        return "Empty! متخازل"
      
    formatted_tasks = ''
    for i, task in enumerate(tasks):
        formatted_tasks += f'{i + 1}- {task.description} - []\n'
    
    return formatted_tasks

def convert_subscriber_profile_to_str(subscriber: Subscriber):
    return  f'''
                ```Default Penalties```
                `Default Yellow Card` 🟨\n `{subscriber.default_yellow_description}`\n                   
                `Default Red Card` 🟥\n `{subscriber.default_red_description}`                    
                
                ```Profile Properties```
                `Default Completion Threshold`: `{subscriber.threshold_percentage}`
                `Banned`: {"🅱️" if subscriber.is_banned else "`Not Banned` 🟩" }
                `Strict Mode`: {"`Enabled` 🟩" if subscriber.strict_mode else "`Disabled` 🟥"}
                `Color Mode`: `{get_color_mode_name(subscriber.color_mode)}`
            '''

def convert_formatted_tasks_to_percentages(formatted_tasks: str) -> list[float]:
    tasks = []
    tasks_str = formatted_tasks.split("\n")
    pattern = r'\[(.*?)\]'
    completion_percentages = re.findall(pattern, formatted_tasks)
    return completion_percentages


# TODO: change it to to_float and throw exception
def is_float(num: str) -> bool:
    try:
        float(num)
        if math.isfinite(float(num)):
            return True
        return False
    
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
    
def is_guild_member(guild_id: str, user_id: str) -> bool:
    guild = bot.get_guild(guild_id)
    return guild.get_member(user_id) is not None

def parse_discord_mention(mention: str):
    # when u mention somebody in discord it uses the format <@user_id> or <@!user_id>
    return mention[3:-1] if mention[2] == '!' else mention[2:-1]

async def get_valid_user(interaction, who):
    if not is_valid_discord_mention(who):
            await interaction.response.send_message("Please Mention a correct discord user", ephemeral=True)
            return
        
    user_id: int = int(parse_discord_mention(who))
    guild_id: int = int(interaction.guild.id)
    if not await is_existing_discord_user(user_id) or not is_guild_member(guild_id, user_id):
        await interaction.response.send_message("Please Mention a correct discord user in this guild", ephemeral=True)
        return

    if not subscribers_access.is_registered_user(user_id, guild_id):
        await interaction.response.send_message(f'{who} is not registered please register using /register',
                                                ephemeral=True)
        return

    return guild_id, user_id