import discord
from discord.ext import commands
from discord import app_commands 

import database
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty

class SubscribersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register")
    async def register(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        new_subscriber = Subscriber(user_id, guild_id)

        try:
            database.subscribe_user(new_subscriber)
            await interaction.response.send_message(
                f"Be Proud, you are a hard worker, you subscribed to the program successfully {interaction.user.mention}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                "You are already subscribed or cannot subscribe again as you are banned!",
                ephemeral=True
            )
    
    # TODO: Unban user

    # TODO: Get Banned users

async def setup(bot):
    await bot.add_cog(SubscribersCog(bot))

