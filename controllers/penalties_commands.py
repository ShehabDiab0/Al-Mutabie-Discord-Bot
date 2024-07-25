import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
from data_access.subscribers_access import is_registered_user, get_subscriber
from data_access.penalties_access import get_penalty, update_subscriber_penalty, get_penalties_for_week, get_subscriber_penalty_history
from data_access.weeks_access import get_current_week
import helpers


class PenaltiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # Penalty Completed
    @app_commands.command(name="finished_penalty")
    @commands.guild_only()
    async def penalty_done(self, interaction: discord.Interaction):
        task_owner_id: str = str(interaction.user.id)
        guild_id: str = str(interaction.guild.id)
        penalty = get_penalty(task_owner_id, guild_id)

        if not is_registered_user(task_owner_id, guild_id):
            await interaction.response.send_message(f"You have to register first before adding any tasks please use /register to register", ephemeral=True)
            return
        
        if penalty:
            penalty.is_done = True
            # update penalty
            update_subscriber_penalty(penalty)
            await interaction.response.send_message(f"Penalty marked as done, Congratulations", ephemeral=True)
        else:
            await interaction.response.send_message(f"No penalty to mark as done", ephemeral=True)


    @app_commands.command(name="mention_penalized_users")
    @commands.guild_only()
    async def mention_penalized_users(self, interaction: discord.Integration):
        guild_id = str(interaction.guild.id)
        week = get_current_week()
        penalties = get_penalties_for_week(week, guild_id)
        if not penalties:
            await interaction.response.send_message("No penalties this week")
            return
        message = "Penalties this week:\n"
        for penalty in penalties:
            user = interaction.guild.get_member(int(penalty.owner_id))
            if not user:
                continue
            message += f"{user.mention} {penalty.description}\n"
        await interaction.response.send_message(message)


    @app_commands.command(name="penalty_history")
    @app_commands.describe(who="mention a user to show their Penalty History")
    @commands.guild_only()
    async def penalty_history(self, interaction: discord.Interaction, who: Optional[str]):
        guild_id = str(interaction.guild.id)
        if not who:
            who = f'<@{interaction.user.id}>'
        user_info = await helpers.get_valid_user(interaction, who)
        # check if who was correct
        if not user_info:
            return
        _, user_id = user_info
        member = interaction.guild.get_member(int(user_id))
        # check if member is in the server
        if not member:
            await interaction.response.send_message("User not found in the server")
            return
        penalties = get_subscriber_penalty_history(get_subscriber(user_id, guild_id))
        if not penalties:
            await interaction.response.send_message(f"No penalties found for {member.mention}, he has a clean record")
            return
        message = f"Penalties for {member.mention}:\n"
        for penalty in penalties:
            color = "red"
            if penalty.is_yellow:
                color = "yellow"
            message += f"- Week {penalty.week_number}: {color} card, {penalty.description}\n"
        await interaction.response.send_message(message)


async def setup(bot):
    await bot.add_cog(PenaltiesCog(bot))