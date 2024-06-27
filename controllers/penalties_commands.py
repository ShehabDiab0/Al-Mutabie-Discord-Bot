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
