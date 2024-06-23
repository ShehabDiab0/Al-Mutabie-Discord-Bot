class Penalty:
    def __init__(self, description: str, is_done: bool, is_yellow: bool, week_number: int, ownder_id: int):
        self.description = description
        self.is_done = is_done
        self.is_yellow = is_yellow
        self.week_number = week_number
        self.ownder_id = ownder_id