import discord
from discord.ext import commands
from discord import app_commands 
from typing import Optional

from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
from models.guild import Guild
from data_access.guilds_access import add_guild, is_registered_guild
from data_access.subscribers_access import *

class SubscribersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register")
    @app_commands.describe(default_yellow_description="Write your default Yellow card description.")
    @app_commands.describe(default_red_description="Write your default Red card description.")
    @app_commands.describe(task_completion_threshold="enter the threshold percentage you want >= 0.5 (default is 0.6) (we apply a penalty if you completed less than the threshold percentage)")
    async def register(self, interaction: discord.Interaction, default_yellow_description: str, default_red_description: str, task_completion_threshold: float = 0.6):
        if task_completion_threshold < 0.5:
            await interaction.response.send_message('يا متخازل ------ Completion Threshold has to be >= 0.5')
            return

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        new_subscriber = Subscriber(user_id, guild_id, default_yellow_description, default_red_description, task_completion_threshold)
        new_guild = Guild(guild_id, reminder_channel_id=str(interaction.guild.system_channel.id))

        if not is_registered_guild(guild_id):
                add_guild(new_guild)

        try:
            subscribe_user(new_subscriber)
            await interaction.response.send_message(
                f"Be Proud, you are a hard worker, you subscribed to the program successfully {interaction.user.mention}",
                ephemeral=True
            )
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                "You are already subscribed or cannot subscribe again as you are banned!",
                ephemeral=True
            )
    
    @app_commands.command(name="update_default_threshold")
    @app_commands.describe(new_threshold="enter the threshold percentage you want >= 0.5 (default is 0.6) (we apply a penalty if you completed less than the threshold percentage)")
    async def update_default_threshold(self, interaction: discord.Interaction, new_threshold: Optional[float] = 0.6):
        if new_threshold < 0.5:
            await interaction.response.send_message('يا متخازل ------ Completion Threshold has to be >= 0.5')
            return
        
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)

        if not is_registered_user(user_id, guild_id):
            await interaction.response.send_message(
                    'You are not registered please register using /register, (you can also choose threshold there)',
                    ephemeral=True
                )
            return
        
        if is_banned_user(user_id, guild_id):
            await interaction.response.send_message(
                    'banned متخازل كبير'
                )
            return
        
        try:
            update_subscriber_threshold(user_id, guild_id, new_threshold)
            await interaction.response.send_message(f'your threshold is now {new_threshold}', ephemeral=True)
        except Exception as e:
            print(e)
        
    @app_commands.command(name="update_default_yellow_penalty")
    @app_commands.describe(default_yellow_description="Write your default Yellow card description.")
    async def update_default_threshold(self, interaction: discord.Interaction, default_yellow_description: str):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)

        if not is_registered_user(user_id, guild_id):
            await interaction.response.send_message(
                    'You are not registered please register using /register, (you can also choose yellow description there)',
                    ephemeral=True
                )
            return
        
        if is_banned_user(user_id, guild_id):
            await interaction.response.send_message(
                    'banned متخازل كبير'
                )
            return
        
        try:
            update_subscriber_yellow_card(user_id, guild_id, default_yellow_description)
            await interaction.response.send_message(f'your new default for yellow is now {default_yellow_description}', ephemeral=True)
        except Exception as e:
            print(e)
    
    

    # TODO: Unban user

    # TODO: Get Banned users

async def setup(bot):
    await bot.add_cog(SubscribersCog(bot))

