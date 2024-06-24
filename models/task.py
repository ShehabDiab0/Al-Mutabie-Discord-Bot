class Task:
    def __init__(self, task_id: int, description: str, week_number: float, owner_id: int, completion_percentage: float = 0.0):
        self.discription = description
        self.completion_percentage = completion_percentage
        self.week_number = week_number
        self.ownder_id = owner_id