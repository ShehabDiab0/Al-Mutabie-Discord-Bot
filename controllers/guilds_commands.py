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

    # TODO: handle the exception correctly
    @app_commands.command(name="set_reminder_channel")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def set_reminder_channel(self, interaction: discord.Interaction):
        user_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        new_channel_id: str = str(interaction.channel_id)
        new_guild = Guild(guild_id, reminder_channel_id=new_channel_id)

        if not is_registered_user(user_id, guild_id) or is_banned_user(user_id, guild_id):
            await interaction.response.send_message('You are not allowed to do this action as you are not registered or banned, please try to register using /register command', ephemeral=True)
            return

        if not guilds_access.is_registered_guild(guild_id):
            guilds_access.add_guild(new_guild)
            await interaction.response.send_message(f'reminder channel set in {interaction.channel.name}')
            return
        
        try:
            guilds_access.update_guild_reminder_channel(guild_id, new_channel_id)
            await interaction.response.send_message(f"reminder channel set to {interaction.channel.name}")
        except Exception as e:
            print(e)
    
    # TODO: handle the exception correctly
    @app_commands.command(name="reset_reminder_channel")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_reminder_channel(self, interaction: discord.Interaction):
        user_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        new_channel_id: str = str(interaction.guild.system_channel.id)
        new_guild = Guild(guild_id, new_channel_id)

        if not is_registered_user(user_id, guild_id) or is_banned_user(user_id, guild_id):
            await interaction.response.send_message('You are not allowed to do this action as you are not registered or banned, please try to register using /register command',
                                                    ephemeral=True)

        if not guilds_access.is_registered_guild(guild_id):
            guilds_access.add_guild(new_guild)
            await interaction.response.send_message(f'reminder channel set in {interaction.channel.name}')
            return
        
        try:
            guilds_access.update_guild_reminder_channel(guild_id, new_channel_id)
            await interaction.response.send_message(f"reminder channel set to {interaction.guild.system_channel.name}")
        except Exception as e:
            print(e)


    @app_commands.command(name="allow_kicks")
    @commands.guild_only()
    async def allow_kicks(self, interaction: discord.Interaction):
        # check if user is a moderator
        if not interaction.user.guild_permissions.kick_members: 
            await interaction.response.send_message('You are not allowed to do this action as you need "kick members" permision')
            return
        guild_id: str = str(interaction.guild.id)
        guilds_access.update_guild_kicks(guild_id=guild_id, is_allowed_kick=True)
        await interaction.response.send_message('The bot can kick users now')


    @app_commands.command(name="disallow_kicks")
    @commands.guild_only()
    async def disallow_kicks(self, interaction: discord.Interaction):
        # check if user is a moderator
        if not interaction.user.guild_permissions.kick_members: 
            await interaction.response.send_message('You are not allowed to do this action as you need "kick members" permision')
            return
        guild_id: str = str(interaction.guild.id)
        guilds_access.update_guild_kicks(guild_id=guild_id, is_allowed_kick=False)
        await interaction.response.send_message('The bot can\'t kick users now')


async def setup(bot):
    await bot.add_cog(GuildsCog(bot))