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
from data_access import weeks_access
from data_access.subscribers_access import is_banned_user, is_registered_user, get_subscribers
import helpers
import UI

import datetime
import client
import matplotlib.pyplot as plt

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="self_report")
    @app_commands.describe(week="Type Tasks of which week")
    @commands.guild_only()
    async def self_report(self,interaction: discord.Interaction, week: int):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        subscriber = Subscriber(user_id, guild_id)
        tasks = tasks_access.get_subscriber_tasks(subscriber, week)
        
        if not tasks:
            await interaction.response.send_message(f"You have no tasks to report", ephemeral=True)
            return
        
        modal = UI.SelfReportModal(tasks=tasks, curr_idx=0)
        await interaction.response.send_modal(modal)



        

    # # TODO: Delete Tasks
    @app_commands.command(name="delete_tasks")
    @commands.guild_only()
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
    @commands.guild_only()
    async def add_multiple_tasks(self, interaction: discord.Interaction, tasks: str):
        task_owner_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        
        if not is_registered_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"You have to register first before adding any tasks please use /register to register", ephemeral=True)
            return

        if is_banned_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"YOU ARE NOT ALLOWED TO USE THIS, YOU ARE BANNED")
            return

        failed_tasks = []
        tasks = tasks.split("/")
        for task_description in tasks:
            if len(task_description) < 1 or len(task_description) > 100: # select menu doesn't like options < 1 or > 100 characters
                failed_tasks.append(task_description)
                continue
            
            
            new_task = Task(guild_id=guild_id, owner_id=task_owner_id, description=task_description, week_number=get_current_week())
            tasks_access.add_task(new_task)
        if len(failed_tasks) == 0:
            await interaction.response.send_message(f"You added {len(tasks)} tasks to your Tasks SUCCESSFULLY! of Week {new_task.week_number}", ephemeral=True)
            return
        
        await interaction.response.send_message(f'''You added {len(tasks) - len(failed_tasks)} tasks to your Tasks SUCCESSFULLY! of Week {new_task.week_number},
                                                some of the tasks weren't added as each task has to contain 1 to 100 chars only
                                                ''', ephemeral=True)
        
    
    # Add Single Task
    @app_commands.command(name="add_single_task")
    @app_commands.describe(task_description="Write Your task here")
    @commands.guild_only()
    async def add_task(self, interaction: discord.Interaction, task_description: str):
        task_owner_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        
        if not is_registered_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"You have to register first before adding any tasks please use /register to register", ephemeral=True)
            return

        if is_banned_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"YOU ARE NOT ALLOWED TO USE THIS, YOU ARE BANNED")
            return

        if len(task_description) < 1 or len(task_description) > 100: # select menu doesn't like options < 1 or > 100 characters
            await interaction.response.send_message(f"Tasks can only contian 1 to 100 characters", ephemeral=True)
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
    @app_commands.describe(who="mention a user to show their tasks")
    @app_commands.describe(week_number="Type Tasks of which week? use 0 for current week")
    @commands.guild_only()
    async def show_tasks(self, interaction: discord.Interaction, who: Optional[str], week_number: Optional[int] = 0):
        if week_number == 0: # special case for current week
            week_number = get_current_week()

        if not who:
            who = interaction.user.mention

        user_info = await helpers.get_valid_user(interaction, who)
        if user_info is None:
            return
        
        guild_id, user_id= user_info
        subscriber: Subscriber = Subscriber(user_id, guild_id)
        tasks = tasks_access.get_subscriber_tasks(subscriber, week_number)
        formatted_tasks = helpers.convert_tasks_to_str(tasks)

        member = interaction.guild.get_member(int(user_id))
        if not member:
            await interaction.response.send_message("This is not a member in this guild.", ephemeral=True)
            return
    
        embed = discord.Embed(title=f'{member.display_name} Tasks of Week {week_number}',
                            description=formatted_tasks,
                            color=member.color)

        if member.avatar is not None:
            embed.set_thumbnail(url=str(member.avatar))
        await interaction.response.send_message(embed=embed)


    # Show tasks for all users in the guild
    @app_commands.command(name="show_tasks_for_all")
    @app_commands.describe(week_number="Type Tasks of which week? use 0 for current week")
    @commands.guild_only()
    async def show_tasks_for_all(self, interaction: discord.Interaction, week_number: Optional[int] = 0):
        if week_number == 0: # special case for current week
            week_number = get_current_week()
        

        guild_id: str = str(interaction.guild.id)
        subscribers = get_subscribers(guild_id)
        if not subscribers:
            await interaction.response.send_message('no subscribers yet', ephemeral=True)
            return
        
        all_tasks_embeds = []
        for subscriber in subscribers:
            tasks = tasks_access.get_subscriber_tasks(subscriber, week_number)
            formatted_tasks = helpers.convert_tasks_to_str(tasks)

            member = interaction.guild.get_member(int(subscriber.user_id))
            if not member:
                continue
            
            embed = discord.Embed(title=f'{member.display_name} Tasks of Week {week_number}',
                                description=formatted_tasks,
                                color=member.color)

            if member.avatar is not None:
                embed.set_thumbnail(url=str(member.avatar))
            all_tasks_embeds.append(embed)
        
        channel = interaction.channel
        while len(all_tasks_embeds) > 10:
            await channel.send(embeds=all_tasks_embeds[:10])
            all_tasks_embeds = all_tasks_embeds[10:]

        await interaction.response.send_message(embeds=all_tasks_embeds)

    @app_commands.command(name="show_week_data")
    @app_commands.describe(week_number="Type Tasks of which week? use 0 for current week")
    @commands.guild_only()
    async def show_week_data(self, interaction: discord.Interaction, week_number: Optional[int] = 0):
        if week_number == 0: # special case for current week
            week_number = get_current_week()
        

        guild_id: str = str(interaction.guild.id)
        subscribers = get_subscribers(guild_id)

        sub_data = {}
        for sub in subscribers:
            tasks = tasks_access.get_subscriber_tasks(sub, week_number)
            total_progress = helpers.get_total_progress(tasks)
            member = interaction.guild.get_member(int(sub.user_id))

            sub_data[member.display_name] = total_progress
        
        # Plotting the Histogram
        fig, ax = plt.subplots()
        ax.bar(sub_data.keys(), sub_data.values())
        ax.set_xlabel('Users')
        ax.set_ylabel('Total Progress')
        ax.set_title(f'Week {week_number} Progress')
        ax.set_ylim(0, 100)  # Set y-axis limit to 100
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('week_progress.png')
        plt.close()
        file = discord.File('week_progress.png')
        await interaction.response.send_message(files=[file])
        
    
    # Update Task
    @app_commands.command(name="update_task")
    @app_commands.describe(week_number="enter the week number to update the task of that week")
    @commands.guild_only()
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

