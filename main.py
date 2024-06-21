import os
import dotenv # type: ignore THIS IS TO FIX PYLANCE ON MY MACHINE
import discord
from discord import app_commands
from discord.ext import commands

def main():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print("BOT IS RUNNING")
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command")
        except Exception as e:
            print(e)

    @bot.tree.command(name="greet")
    async def greet(interaction: discord.Interaction):
        await interaction.response.send_message(f"Scream My Soldier {interaction.user.mention}", ephemeral=True)

    @bot.tree.command(name="mention")
    @app_commands.describe(who = "who")
    async def mention(interaction: discord.Interaction, who: str):
        await interaction.response.send_message(f"Hey Soldier{who}")

    dotenv.load_dotenv()
    bot.run(os.getenv("API_TOKEN"))


if __name__ == "__main__":
    main()