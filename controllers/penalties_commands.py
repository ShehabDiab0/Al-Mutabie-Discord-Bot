import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
from data_access.subscribers_access import is_registered_user
from data_access.penalties_access import get_penalty, update_subscriber_penalty, get_penalties_for_week
from data_access.weeks_access import get_current_week
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


    # TODO: User Penalty History
    @app_commands.command(name="penalty_history")
    @app_commands.describe(who="mention a user to show their Penalty History")
    @commands.guild_only()
    async def penalty_history(self, interaction: discord.Interaction, who: Optional[str]):
        pass


async def setup(bot):
    await bot.add_cog(PenaltiesCog(bot))