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
import helpers
import UI

class SubscribersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register")
    @commands.guild_only()
    async def register(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        new_guild = Guild(guild_id, reminder_channel_id=str(interaction.guild.system_channel.id))

        if not is_registered_guild(guild_id):
                add_guild(new_guild)
        
        if is_registered_user(user_id, guild_id):
            await interaction.response.send_message(
                "You are already subscribed or cannot subscribe again as you are banned! (you can edit profile using /edit_profile command)",
                ephemeral=True
            )
            return

        modal = UI.RegisterationModal()
        await interaction.response.send_modal(modal)

    @app_commands.command(name="show_profile")
    @app_commands.describe(who="mention a user to Show their Profile")
    @commands.guild_only()
    async def show_profile(self, interaction: discord.Interaction, who: Optional[str]):
        if not who:
            who = f'<@{interaction.user.id}>'

        user_info = await helpers.get_valid_user(interaction, who)
        if user_info is None:
            return
        
        guild_id, user_id= user_info
        subscriber: Subscriber = get_subscriber(user_id, guild_id)
        formatted_profile = helpers.convert_subscriber_profile_to_str(subscriber)

        member = interaction.guild.get_member(int(user_id))
        embed = discord.Embed(title=f'{member.display_name} Profile',
                              description=formatted_profile,
                              color=member.color)
        if member.avatar is not None:
            embed.set_thumbnail(url=str(member.avatar))
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="edit_profile")
    @commands.guild_only()
    async def edit_profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)

        if not is_registered_user(user_id, guild_id):
            await interaction.response.send_message('You are not registered please register using /register',
                                                    ephemeral=True)
            return
        
        if is_banned_user(user_id, guild_id):
            await interaction.response.send_message('Banned users are not allowed to edit their profile.',
                                                    ephemeral=True)
            return

        modal = UI.EditProfileModal()
        await interaction.response.send_modal(modal)


    @app_commands.command(name='unban_user')
    @app_commands.describe(who="mention a user to unban")
    @app_commands.checks.has_permissions(administrator=True)
    @commands.guild_only()
    async def unban_user(self, interaction: discord.Interaction, who: Optional[str]):
        if not who:
            who = f'<@{interaction.user.id}>'

        user_info = await helpers.get_valid_user(interaction, who)
        if user_info is None:
            return
        
        guild_id, user_id= user_info
        update_ban_status(user_id, guild_id, is_banned=False)
        await interaction.response.send_message(f'{who} is Unbanned Successfully :^)')

    @unban_user.error
    async def subscriber_error_handle(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message('You don\'t have permissions to use this command.')
    # TODO: Get Banned users


    @app_commands.command(name="mention_subscribers")
    @commands.guild_only()
    async def mention_subscribers(self, interaction: discord.Integration):
        guild_id = str(interaction.guild.id)
        subscribers = get_subscribers(guild_id)
        if not subscribers:
            await interaction.response.send_message("No one is subscribed. use /register (or everyone is banned :) )")
            return
        message = ""
        for subscriber in subscribers:
            user = interaction.guild.get_member(int(subscriber.user_id))
            if not user:
                continue
            message += f"{user.mention}"
        await interaction.response.send_message(message)

async def setup(bot):
    await bot.add_cog(SubscribersCog(bot))

