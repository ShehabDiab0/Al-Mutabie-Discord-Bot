import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
from data_access.subscribers_access import is_registered_user
from data_access.penalties_access import get_penalty, update_subscriber_penalty
class PenaltiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # Penalty Completed
    @app_commands.command(name="penalty_done")
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



async def setup(bot):
    await bot.add_cog(PenaltiesCog(bot))