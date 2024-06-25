import discord
from discord.ext import commands
from discord import app_commands


from client import bot
import database


from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
import helpers
import UI

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # # TODO: Delete Tasks
    # @app_commands.command(name="delete_tasks")
    # async def delete_tasks(self, ctx):
        
    #     ui = UI.DeleteSelectMenu(0, 0)
    #     await ("Choose the task you want to delete", view=ui)

    # TODO: Add Multiple Tasks
    @app_commands.command(name="add_multiple_tasks")
    @app_commands.describe(tasks="Write Your tasks here separated by /")
    async def add_multiple_tasks(self, interaction: discord.Interaction, tasks: str):
        task_owner_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        
        if not database.is_registered_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"You have to register first before adding any tasks please use /register to register")
            return

        if database.is_banned_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"YOU ARE NOT ALLOWED TO USE THIS, YOU ARE BANNED")
            return

        tasks = tasks.split("/")
        for task_description in tasks:
            new_task = Task(guild_id=guild_id, owner_id=task_owner_id, description=task_description, week_number=database.get_current_week())
            try:
                database.add_task(new_task)
            except Exception as e:
                print(e)
                await interaction.response.send_message(f"Failed to add this task", ephemeral=True)

        await interaction.response.send_message(f"You added {len(tasks)} tasks to your Tasks SUCCESSFULLY! of Week {new_task.week_number}", ephemeral=True)
    
    # Add Single Task
    @app_commands.command(name="add_single_task")
    @app_commands.describe(task_description="Write Your task here")
    async def add_task(self, interaction: discord.Interaction, task_description: str):
        task_owner_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        
        if not database.is_registered_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"You have to register first before adding any tasks please use /register to register")
            return

        if database.is_banned_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"YOU ARE NOT ALLOWED TO USE THIS, YOU ARE BANNED")
            return

        new_task = Task(guild_id=guild_id, owner_id=task_owner_id, description=task_description, week_number=database.get_current_week())
        try:
            database.add_task(new_task)
            await interaction.response.send_message(f"You added {task_description} to your Tasks SUCCESSFULLY! of Week {new_task.week_number}", ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Failed to add this task", ephemeral=True)

    # Show Tasks
    @app_commands.command(name="show_tasks")
    @app_commands.describe(who="mention a user to know their tasks")
    @app_commands.describe(week_number="Type Tasks of which week? use 0 for current week")
    async def show_tasks(self, interaction: discord.Interaction, who: str, week_number: int):
        if week_number == 0: # special case for current week
            week_number = database.get_current_week()

        user_id = who[2:-1] # when u mention somebody in discord it uses the format <@user_id>
        guild_id: str = str(interaction.guild.id)
        subscriber: Subscriber = Subscriber(user_id, guild_id)

        tasks = database.get_subscriber_tasks(subscriber, week_number)
        formatted_tasks = helpers.convert_tasks_to_str(tasks)

        member = interaction.guild.get_member(int(user_id))
        embed = discord.Embed(title=f'{member.display_name} Tasks of Week {week_number}',
                              description=formatted_tasks,
                              color=member.color)
        embed.set_thumbnail(url=str(member.avatar))
        await interaction.response.send_message(embed=embed)
        




async def setup(bot):
    await bot.add_cog(TasksCog(bot))

