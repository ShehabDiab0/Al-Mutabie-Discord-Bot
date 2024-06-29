class Penalty:
    def __init__(self,penalty_id:int, description: str, is_done: bool, is_yellow: bool, week_number: int, owner_id: int):
        self.penalty_id = penalty_id
        self.description = description
        self.is_done = is_done
        self.is_yellow = is_yellow
        self.week_number = week_number
        self.owner = owner_id