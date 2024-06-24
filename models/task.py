class Task:
    def __init__(self, guild_id, owner_id: int, description: str, week_number: float, completion_percentage: float = 0.0):
        self.description = description
        self.completion_percentage = completion_percentage
        self.week_number = week_number
        self.guild_id = guild_id
        self.owner_id = owner_id