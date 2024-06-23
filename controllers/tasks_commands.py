import discord
from discord.ext import commands
from discord import app_commands 

from client import bot
import database

from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty


class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Add Tasks


    # TODO: Show Tasks
    # @bot.tree.command(name="tasks")
    # @app_commands.describe(who="who")
    # @app_commands.describe(task_num="task_number")
    # async def show_tasks(interaction: discord.Interaction, who: str, task_num: int):
    #     pass

    # TODO: Delete Tasks
    @app_commands.command(name="delete_task")
    @app_commands.describe(who="who to mention")
    @app_commands.describe(task_number="task number")
    async def delete_task(self, interaction: discord.Interaction, who: str, task_number: int):
        await interaction.response.send_message(f"Hey Soldier {who}, You Deleted Task {task_number}")



async def setup(bot):
    await bot.add_cog(TasksCog(bot))

