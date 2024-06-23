class Subscriber:
    def __init__(self, user_id: str, guild_id: str, is_activated: bool=True, is_allowed_to_register: bool=True):
        self.user_id = user_id
        self.guild_id = guild_id
        self.is_activated = is_activated
        self.is_allowed_to_register = is_allowed_to_register
