class Subscriber:
    def __init__(self, user_id: str, guild_id: str, default_yellow_description: str = "",
                 default_red_description: str = "", threshold_percentage: float = 60.0, strict_mode: bool = True,
                 is_banned: bool = False):
        self.user_id = user_id
        self.guild_id = guild_id
        self.default_yellow_description = default_yellow_description
        self.default_red_description = default_red_description
        self.threshold_percentage = threshold_percentage
        self.strict_mode = strict_mode
        self.is_banned = is_banned
