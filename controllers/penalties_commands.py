import discord
from discord.ext import commands
from discord import app_commands 
from client import kick
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
from data_access import weeks_access, penalties_acess, subscribers_access
class PenaltiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# TODO: check if previous yellow tasks are completed
# TODO: reminders and guild scheduling


    def weekly_check(self, guild_id) -> None:
        week_num = weeks_access.get_current_week()
        # get all users having this guild_id and not is_banned in a list of ids
        subscribers = []
        for subscriber in subscribers:
            card = self.check_user(subscriber, week_num)
            if card:
                previous_card = penalties_acess.get_subscriber_penalty_history(subscriber=subscriber)[-1]
                is_yellow = 1
                desc = subscriber.default_yellow_penalty_description
                if previous_card:
                    # red card
                    is_yellow = 0
                    kick(subscriber.user_id, guild_id)
                    desc = subscriber.default_red_penalty_description
                # add penalty in db
                penalty = Penalty(description=desc, is_yellow=is_yellow, week_number=week_num, guild_id=guild_id, owner_id=subscriber.user_id)
                penalties_acess.add_penalty(penalty)


    # checks user weekly progress and returns true if he should recieve a card
    def check_user(self, subscriber, week_num) -> bool:
        tasks = subscribers_access.get_subscriber_tasks(subscriber, week_num)
        total = len(tasks)
        if not total:
            return True
        completed = 0.0
        for task in tasks:
            completed += task.completion_percentage
        return completed / total < subscriber.threshold




async def setup(bot):
    await bot.add_cog(PenaltiesCog(bot))
