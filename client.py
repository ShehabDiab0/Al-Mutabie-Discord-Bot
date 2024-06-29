import discord
from discord.ext import commands
from discord import app_commands 
import dotenv # type: ignore
import os
import database
from data_access import weeks_access
from data_access.guilds_access import get_channel_id

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import datetime
import asyncio

##################### BOT SETTINGS #####################
LOCATION = "Africa/Cairo"
TIMEZONE = pytz.timezone(LOCATION)
YELLOW_THRESHOLD = 3
RED_THRESHOLD = 5
TIME_ALLOWED = 5
DAY_TO_RESET = "thu"
########################################################


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
scheduler = AsyncIOScheduler()


# loading cogs to sync other files commands
async def load_cogs():
    for filename in os.listdir('./controllers'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'controllers.{filename[:-3]}')
                print(f'Loaded extension: {filename}')
            except Exception as e:
                print(f'Failed to load extension {filename}: {e}')

# ------------------------ Running the bot ------------------------
# running the bot
def run_bot():
    database.init_db()
    dotenv.load_dotenv()

    today = datetime.datetime.now()
    today = TIMEZONE.localize(today)
    # if today is not Thursday (0 is Monday, 6 is Sunday)
    if weeks_access.get_current_week() == None:
        weeks_access.add_week() 

    bot.run(os.getenv("API_TOKEN"))

    
    
# ------------------------ GENERAL commands and events ------------------------

@bot.event
async def on_ready():
    print("BOT IS RUNNING")
    await load_cogs()
    await run_scheduler()
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


# reminder
async def reminder(user_id: str, guild_id: str):
    guild_id = int(guild_id)
    user_id = int(user_id)
    channel_id = int(get_channel_id(guild_id))
    # Fetch the user object using the user ID
    user = await bot.fetch_user(user_id)
    
    # Fetch the channel object using the channel ID
    channel = bot.get_channel(channel_id)
    
    if channel and user:  # Check if both the channel and user were found
        # Send a message in the channel mentioning the user
        await channel.send(f"{user.mention}, don't forget your tasks :)")
    else:
        print("User or channel not found.")

class CustomContext:
    def __init__(self, guild, channel):
        self.guild = guild
        self.channel = channel

    async def send(self, content):
        await self.channel.send(content)


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(user_id: str, guild_id: str):
    reason = "Got a red card!"
    try:
        # Convert IDs to integers
        guild_id = int(guild_id)
        user_id = int(user_id)
        channel_id = int(get_channel_id(guild_id))

        # Fetch the guild
        guild = bot.get_guild(guild_id)
        if not guild:
            print('Guild not found.')
            return

        # Fetch the channel using the channel_id
        channel = guild.get_channel(channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            print('Channel not found or is not a text channel.')
            return

        # Create a custom context-like object
        custom_ctx = CustomContext(guild, channel)

        # Fetch the member
        member = guild.get_member(user_id)
        if not member:
            await custom_ctx.send('Member not found.')
            return

        # Kick the member
        await member.kick(reason=reason)
        await custom_ctx.send(f'{member.mention} has been kicked for: {reason}')

    except ValueError:
        print('Invalid guild_id, user_id, or channel_id.')
    except discord.Forbidden:
        await custom_ctx.send('I do not have permission to kick this user.')
    except discord.HTTPException as e:
        await custom_ctx.send(f'Failed to kick the user. Error: {e}')


# TODO: Get Task Instructions


# ------------------------ Scheduling functions/commands ------------------------

async def run_scheduler():
    scheduler.start()
    scheduler.add_job(weeks_access.add_week, trigger='cron', day_of_week=DAY_TO_RESET, timezone=TIMEZONE)
    # scheduler.add_job(weeks_access.add_week, trigger='cron',second='*', timezone=TIMEZONE)
    #print all the jobs
    print("Scheduler started")

@bot.tree.command(name="pause_scheduler")
async def pause_scheduler(interaction: discord.Interaction):
    scheduler.pause()
    await interaction.response.send_message("Scheduler paused")

@bot.tree.command(name="resume_scheduler")
async def resume_scheduler(interaction: discord.Interaction):
    scheduler.resume()
    await interaction.response.send_message("Scheduler resumed")


    
