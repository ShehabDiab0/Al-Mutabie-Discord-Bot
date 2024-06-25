from models.task import Task

def convert_tasks_to_str(tasks: list[Task]) -> str:
        if len(tasks) == 0:
            return "Empty! متخازل"
        
        formatted_tasks = ''
        for i, task in enumerate(tasks):
            formatted_tasks += f'{i + 1}- {task.description} - {task.completion_percentage}%\n'

        return formatted_tasks