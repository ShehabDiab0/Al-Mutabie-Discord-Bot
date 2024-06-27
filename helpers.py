from models.task import Task
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

def convert_formatted_tasks_to_percentages(formatted_tasks: str) -> list[float]:
    tasks = []
    tasks_str = formatted_tasks.split("\n")
    pattern = r'\[(.*?)\]'
    completion_percentages = re.findall(pattern, formatted_tasks)
    return completion_percentages

    