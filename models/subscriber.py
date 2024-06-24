class Subscriber:
    def __init__(self, user_id: str, guild_id: str, is_banned: bool=False):
        self.user_id = user_id
        self.guild_id = guild_id
        self.is_banned = is_banned
