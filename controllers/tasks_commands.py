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


    # TODO: Show Tasks
    # @bot.tree.command(name="tasks")
    # @app_commands.describe(who="who")
    # @app_commands.describe(task_num="task_number")
    # async def show_tasks(self, interaction: discord.Interaction, who: str, task_num: int):
    #     pass

    # TODO: Delete Tasks
    @app_commands.command(name="delete_task")
    @app_commands.describe(who="who to mention")
    @app_commands.describe(task_number="task number")
    async def delete_task(self, interaction: discord.Interaction, who: str, task_number: int):
        await interaction.response.send_message(f"Hey Soldier {who}, You Deleted Task {task_number}")

    
    @app_commands.command(name="add_task")
    @app_commands.describe(task_description="Write Your task here")
    async def add_task(self, interaction: discord.Interaction, task_description: str):
        task_owner_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        new_task = Task(guild_id=guild_id, owner_id=task_owner_id, description=task_description, week_number=database.get_current_week())
        try:
            database.add_task(new_task)
            await interaction.response.send_message(f"You added {task_description} to your Tasks SUCCESSFULLY! of Week {new_task.week_number}", ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Failed to add this task", ephemeral=True)



async def setup(bot):
    await bot.add_cog(TasksCog(bot))

