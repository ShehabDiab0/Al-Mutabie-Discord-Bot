from datetime import datetime
class Week:
    def __init__(self, week_number: int, start_date: datetime, end_date: datetime):
        self.week_number = week_number
        self.start_date = start_date
        self.end_date = end_date