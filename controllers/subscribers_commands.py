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
    async def register(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        new_guild = Guild(guild_id)

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
    @app_commands.describe(who="mention a user to know their tasks")
    async def show_profile(self, interaction: discord.Interaction, who: Optional[str] = "-1"):
        if who == "-1":
            who = f'<@{interaction.user.id}>'


        if not helpers.is_valid_discord_mention(who):
            await interaction.response.send_message("Please Mention a correct discord user", ephemeral=True)
            return
        
        user_id = who[3:-1] if who[2] == '!' else who[2:-1] # when u mention somebody in discord it uses the format <@user_id> or <@!user_id>
        if not await helpers.is_existing_discord_user(user_id):
            await interaction.response.send_message("Please Mention a correct discord user", ephemeral=True)
            return

        guild_id: str = str(interaction.guild.id)
        if not is_registered_user(user_id, guild_id):
            await interaction.response.send_message(
                    'You are not registered please register using /register',
                    ephemeral=True
                )
            return

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
    async def edit_profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)

        if not is_registered_user(user_id, guild_id):
            await interaction.response.send_message(
                    'You are not registered please register using /register',
                    ephemeral=True
                )
            return
        
        if is_banned_user(user_id, guild_id):
            await interaction.response.send_message('Banned users are not allowed to edit their profile.',
                                                    ephemeral=True)

        modal = UI.EditProfileModal()
        await interaction.response.send_modal(modal)


    # TODO: Unban user

    # TODO: Get Banned users

async def setup(bot):
    await bot.add_cog(SubscribersCog(bot))

