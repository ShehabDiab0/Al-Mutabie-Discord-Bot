import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands


from client import bot


from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
from database import connection
from data_access import tasks_access
from data_access.weeks_access import get_current_week
from data_access.subscribers_access import is_banned_user, is_registered_user
import helpers
import UI

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # TODO: Self Report
    @app_commands.command(name="self_report")
    async def self_report(self,interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        subscriber = Subscriber(user_id, guild_id)
        tasks = tasks_access.get_subscriber_tasks(subscriber, get_current_week())
        
        if not tasks:
            await interaction.response.send_message(f"You have no tasks to report", ephemeral=True)
            return

        week_number = get_current_week()
        user_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        subscriber: Subscriber = Subscriber(user_id, guild_id)

        tasks = tasks_access.get_subscriber_tasks(subscriber, week_number)
        
        modal = UI.SelfReportModal(tasks=tasks)
        await interaction.response.send_modal(modal)
        # await interaction.response.send_message("Select a Task to Report", ephemeral=True)



        

    # # TODO: Delete Tasks
    @app_commands.command(name="delete_tasks")
    async def delete_tasks(self, interaction: discord.Interaction):
        # Show him his tasks
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        subscriber = Subscriber(user_id, guild_id)
        tasks = tasks_access.get_subscriber_tasks(subscriber, get_current_week())
        formatted_tasks = helpers.convert_tasks_to_str(tasks)
        if not formatted_tasks:
            await interaction.response.send_message(f"You have no tasks to delete", ephemeral=True)
            return
        
        # Show him Selection
        view = UI.DeleteTaskView(tasks)
        await interaction.response.send_message("Select a Task to Delete", view=view, ephemeral=True)

        

    # Add Multiple Tasks
    @app_commands.command(name="add_multiple_tasks")
    @app_commands.describe(tasks="Write Your tasks here separated by /")
    async def add_multiple_tasks(self, interaction: discord.Interaction, tasks: str):
        task_owner_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        
        if not is_registered_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"You have to register first before adding any tasks please use /register to register")
            return

        if is_banned_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"YOU ARE NOT ALLOWED TO USE THIS, YOU ARE BANNED")
            return

        tasks = tasks.split("/")
        for task_description in tasks:
            new_task = Task(guild_id=guild_id, owner_id=task_owner_id, description=task_description, week_number=get_current_week())
            try:
                tasks_access.add_task(new_task)
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
        
        if not is_registered_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"You have to register first before adding any tasks please use /register to register")
            return

        if is_banned_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"YOU ARE NOT ALLOWED TO USE THIS, YOU ARE BANNED")
            return

        new_task = Task(guild_id=guild_id, owner_id=task_owner_id, description=task_description, week_number=get_current_week())
        try:
            tasks_access.add_task(new_task)
            await interaction.response.send_message(f"You added {task_description} to your Tasks SUCCESSFULLY! of Week {new_task.week_number}", ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Failed to add this task", ephemeral=True)

    # Show Tasks
    @app_commands.command(name="show_tasks")
    @app_commands.describe(who="mention a user to know their tasks")
    @app_commands.describe(week_number="Type Tasks of which week? use 0 for current week")
    async def show_tasks(self, interaction: discord.Interaction, week_number: Optional[int] = 0, who: Optional[str] = "-1"):
        if week_number == 0: # special case for current week
            week_number = get_current_week()

        if who == "-1":
            who = f'<@{interaction.user.id}>'

        guild_id: str = str(interaction.guild.id)
        user_id = who[3:-1] if user_id[2] == '!' else who[2:-1] # when u mention somebody in discord it uses the format <@user_id> or <@!user_id>

        if not helpers.is_valid_discord_mention(who) or not await helpers.is_existing_discord_user(user_id):
            await interaction.response.send_message("Please Mention a correct discord user", ephemeral=True)
            return
        
        subscriber: Subscriber = Subscriber(user_id, guild_id)
        tasks = tasks_access.get_subscriber_tasks(subscriber, week_number)
        formatted_tasks = helpers.convert_tasks_to_str(tasks)

        member = interaction.guild.get_member(int(user_id))
        embed = discord.Embed(title=f'{member.display_name} Tasks of Week {week_number}',
                            description=formatted_tasks,
                            color=member.color)
        embed.set_thumbnail(url=str(member.avatar))
        await interaction.response.send_message(embed=embed)
        

    # Update Task
    @app_commands.command(name="update_task")
    @app_commands.describe(week_number="enter the week number to update the task of that week")
    async def update_task(self, interaction: discord.Interaction, week_number: Optional[int] = 0):
        # Show him his tasks
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        subscriber = Subscriber(user_id, guild_id)
        if(week_number == 0):
            week_number = get_current_week()
        tasks = tasks_access.get_subscriber_tasks(subscriber, week_number)
        if not tasks:
            await interaction.response.send_message(f"You have no tasks to update", ephemeral=True)
            return
        
        # Show him Selection
        view = UI.UpdateTaskView(tasks)
        await interaction.response.send_message("Select a Task to Update", view=view, ephemeral=True)

    

async def setup(bot):
    await bot.add_cog(TasksCog(bot))

