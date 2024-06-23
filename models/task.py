class Task:
    def __init__(self, task_id: int, description: str, completion_percentage: float, week_number: float, owner_id: int):
        self.task_id = task_id
        self.discription = description
        self.completion_percentage = completion_percentage
        self.week_number = week_number
        self.ownder_id = owner_id