import discord
from discord.ext import commands
from discord import app_commands 

from client import bot
from data_access import guilds_access

from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
from models.guild import Guild
from data_access.subscribers_access import is_banned_user, is_registered_user

class GuildsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_reminder_channel")
    async def set_reminder_channel(self, interaction: discord.Interaction):
        user_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        new_channel_id: str = str(interaction.channel_id)
        new_guild = Guild(guild_id, reminder_channel_id=new_channel_id)

        if not is_registered_user(user_id, guild_id) or is_banned_user(user_id, guild_id):
            await interaction.response.send_message('You are not allowed to do this action as you are not registered or banned, please try to register using /register command')

        if not guilds_access.is_registered_guild(guild_id):
            guilds_access.add_guild(new_guild)
            await interaction.response.send_message(f'reminder channel set in {interaction.channel.name}')
            return
        
        try:
            guilds_access.update_guild_reminder_channel(guild_id, new_channel_id)
            await interaction.response.send_message(f"reminder channel set to {interaction.channel.name}")
        except Exception as e:
            print(e)



async def setup(bot):
    await bot.add_cog(GuildsCog(bot))