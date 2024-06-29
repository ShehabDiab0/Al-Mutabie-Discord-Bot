class Penalty:
    def __init__(self, guild_id:str, description: str, is_done: bool, is_yellow: bool, week_number: int, owner_id: int, penalty_id:int = None):
        self.penalty_id = penalty_id
        self.guild_id = guild_id
        self.description = description
        self.is_done = is_done
        self.is_yellow = is_yellow
        self.week_number = week_number
        self.owner_id = owner_id