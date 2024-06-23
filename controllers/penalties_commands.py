import discord
from discord.ext import commands
from discord import app_commands 

import database
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty

class PenaltiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot





async def setup(bot):
    await bot.add_cog(PenaltiesCog(bot))
