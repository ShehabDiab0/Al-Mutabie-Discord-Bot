import discord
from discord.ext import commands, tasks
from discord import app_commands 
import dotenv # type: ignore
import os
import database
from data_access import penalties_access, weeks_access
from data_access.guilds_access import get_channel_id
from data_access import weeks_access, subscribers_access, guilds_access, tasks_access
from models.subscriber import Subscriber
from models.penalty import Penalty
from models.guild import Guild
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import sys
import asyncio
import json
import os
from datetime import datetime, timedelta

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

    today = datetime.now()
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
    finally:
        
        # start a periodic check
        daily_check.start()

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


# send card
async def send_card(user_id: str, guild_id: str, penalty: Penalty):
    guild_id = int(guild_id)
    user_id = int(user_id)
    channel_id = int(get_channel_id(guild_id))
    # Fetch the user object using the user ID
    user = await bot.fetch_user(user_id)
    # Fetch the channel object using the channel ID
    channel = bot.get_channel(channel_id)
    card = "received a red card \U0001F7E5"
    if penalty.is_yellow:
        card = "received a yellow card \U0001F7E8"
    if channel and user:  # Check if both the channel and user were found
        # Send a message in the channel mentioning the user
        await channel.send(f"{user.mention} {card} for not completing his tasks, His punishment will be {penalty.description}")
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

#----------------------------penalties-------------------------------
    
LAST_RUN_FILE = sys.argv[2] if len(sys.argv) >= 3 else "last_run.json"


def load_last_run_time():
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['last_run']).date()  # Load and return only the date
    return None


def save_last_run_time(date):
    with open(LAST_RUN_FILE, 'w') as f:
        json.dump({'last_run': date.strftime('%Y-%m-%d')}, f)


async def daily_task(day: int):
    
    penalties = Penalties()
    
    penalties.run_penalties(day)
    print("Running daily task")


# A periodic check to ensure daily execution if the bot stays online
@tasks.loop(hours=1)
async def daily_check():
    last_run = load_last_run_time()
    today = datetime.now().date()

    if last_run is None or today > last_run:
        await daily_task(today.weekday())
        save_last_run_time(today)


@daily_check.before_loop
async def before_daily_check():
    await bot.wait_until_ready()



class Penalties():

# TODO: reminders and guild scheduling

    def run_penalties(self, day: int) -> None:
        print("running penalties")
        reminder_guilds, apply_guilds = guilds_access.get_today_guilds(day)
        for guild in reminder_guilds:
            self.weekly_check(guild, True)
        for guild in apply_guilds:
            self.weekly_check(guild, False)


    def weekly_check(self, guild: Guild, remind: bool) -> None:
        guild_id = guild.guild_id
        print("weekly check")
        week_num = weeks_access.get_current_week()
        # get all users having this guild_id and not is_banned in a list of ids
        subscribers = subscribers_access.get_subscribers(guild_id)
        print(len(subscribers))
        for subscriber in subscribers:
            print("subscriber: ", subscriber.user_id)
            previous_card = penalties_access.get_subscriber_penalty_history(subscriber=subscriber)
            if previous_card:
                previous_card = previous_card[-1]
            else:
                previous_card = None
            card = self.check_user(subscriber, week_num - 1, previous_card)
            if card:
                if remind:
                    print('remind')
                    bot.loop.create_task(reminder(subscriber.user_id, guild_id))
                    return
                is_yellow = 1
                desc = subscriber.default_yellow_description
                if previous_card and ((previous_card.week_number - week_num) == 1):
                    # red card
                    is_yellow = 0
                    if guild.allow_kicks:
                        print('kick')
                        bot.loop.create_task(kick(subscriber.user_id, guild_id))
                    desc = subscriber.default_red_description
                    subscribers_access.ban_user(subscriber)
                # add penalty in db
                penalty = Penalty(description=desc, is_yellow=is_yellow, week_number=week_num, guild_id=guild_id, owner_id=subscriber.user_id, is_done=False)
                bot.loop.create_task(send_card(subscriber.user_id, guild_id, penalty))
                penalties_access.add_penalty(penalty)


    # checks user weekly progress and returns true if he should receive a card
    def check_user(self, subscriber: Subscriber, week_num: int, previous_card: Penalty) -> bool:
        print("check user")
        if previous_card and not previous_card.is_done:
            return True
        tasks = tasks_access.get_subscriber_tasks(subscriber, week_num)
        total = len(tasks)
        if not total:
            return True
        completed = 0.0
        for task in tasks:
            completed += task.completion_percentage
        return completed / total < (subscriber.threshold_percentage * 100)

# ------------------------ Instructions ------------------------
@bot.tree.command(name="instructions")
async def instructions(interaction: discord.Interaction):
    info = '''**Commands Description:**
            1. /register: To register to the bot\n 
            2. To show someone Profile or your Profile use /show_profile\n
            3. To edit your profile use /edit_profile\n
            4. To add a task use /add_single_task\n
            5. To add multiple tasks use /add_multiple_tasks\n
            6. To show Someone or your tasks use /show_tasks\n
            7. To delete a task use /delete_task\n
            8. To update a task use /update_task\n
            9. To do a self report use /self_report\n
            10. To check your penalty done use /penalty_done\n
            **Rules:**
            1. When do we apply penalties? ==> Every Sunday @ 12:00 AM
    '''
    embed = discord.Embed(title=f'Instructions and Rules',
                              description=info,
                              color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)
