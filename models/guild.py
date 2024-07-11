class Guild:
    def __init__(self, guild_id: str, reminder_channel_id: str, allow_kicks: bool = False, reminder_day: int = 0, offset_days: int = 2):
        self.guild_id = guild_id
        self.reminder_channel_id = reminder_channel_id
        self.allow_kicks = allow_kicks
        self.reminder_day = reminder_day
        self.offset_days = offset_days