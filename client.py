import discord
from discord.ext import commands
from discord import app_commands 
import dotenv
import os
import database

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# loading cogs to sync other files commands
async def load_cogs():
    for filename in os.listdir('./controllers'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'controllers.{filename[:-3]}')
                print(f'Loaded extension: {filename}')
            except Exception as e:
                print(f'Failed to load extension {filename}: {e}')

# ------------------------ GENERAL commands and events ------------------------

@bot.event
async def on_ready():
    print("BOT IS RUNNING")
    await load_cogs()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command")
    except Exception as e:
        print(e)

# Greet Command
@bot.tree.command(name="greet")
async def greet(interaction: discord.Interaction):
    await interaction.response.send_message(f"Scream My Soldier {interaction.user.mention}", ephemeral=True)


# Testing mention command
@bot.tree.command(name="mention")
@app_commands.describe(who="who")
async def mention(interaction: discord.Interaction, who: str):
    await interaction.response.send_message(f"Hey Soldier{who}")



# TODO: Get Task Instructions

def run_bot():
    database.init_db()
    dotenv.load_dotenv()
    bot.run(os.getenv("API_TOKEN"))