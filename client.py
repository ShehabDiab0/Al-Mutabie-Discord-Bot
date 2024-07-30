import discord
from discord.ext import commands, tasks
from discord import app_commands 
import dotenv # type: ignore
import os
from data_access import penalties_access, weeks_access
from data_access.guilds_access import get_channel_id
from data_access import weeks_access, subscribers_access, guilds_access, tasks_access
from models.subscriber import Subscriber
from models.penalty import Penalty
from models.guild import Guild
import sys
import json
import os
from datetime import datetime, timedelta
from constants import TIMEZONE
from penalty_scheduler import Penalties



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

# ------------------------ Running the bot ------------------------
# running the bot
def run_bot():
    dotenv.load_dotenv()
    today = datetime.now()
    today = TIMEZONE.localize(today)
    bot.run(os.getenv("API_TOKEN"))

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
    finally:
        
        # start a periodic check
        daily_check.start()

# Greet Command
@bot.tree.command(name="greet")
async def greet(interaction: discord.Interaction):
    await interaction.response.send_message(f"Scream My Soldier {interaction.user.mention}", ephemeral=True)


# Testing mention command
@bot.tree.command(name="mention")
@commands.guild_only()
@app_commands.describe(who="who")
async def mention(interaction: discord.Interaction, who: str):
    await interaction.response.send_message(f"Hey Soldier{who}")


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
    penalties = Penalties(bot)
    if weeks_access.has_week_ended():
        print('Adding a new week')
        weeks_access.add_week()
        penalties.remind_everyone()

    penalties.run_penalties(day)
    print("Running daily task for day:", day)


# A periodic check to ensure daily execution if the bot stays online
@tasks.loop(hours=1)
async def daily_check():
    last_run = load_last_run_time()
    today = datetime.now().date()

    if last_run is None or today > last_run:
        await daily_task((today.weekday() - 4) % 7)
        save_last_run_time(today)


@daily_check.before_loop
async def before_daily_check():
    await bot.wait_until_ready()


# ------------------------ Instructions ------------------------
@bot.tree.command(name="help")
@commands.guild_only()
async def instructions(interaction: discord.Interaction):
    info = '''
**Commands Description:**
1. /register: To register to the bot
2. To show someone Profile or your Profile use /show_profile, Parameters: who
3. To edit your profile use /edit_profile (you can edit threshold, default yellow card, default red card)
4. To add a task use /add_single_task, The tasks should be 1 to 100 chars each
5. To add multiple tasks use /add_multiple_tasks, Please seperate them by dashes, The tasks should be 1 to 100 chars each
6. To show Someone or your tasks use /show_tasks, Parameters: who, week_number
7. To show tasks for all subscribers use /show_tasks_for_all, parameters: week_number
8. To delete multiple tasks use /delete_task
9. To update a single task use /update_task, Parameters: week_number
10. To quickly update your week progress or tasks completion percentages use /self_report, Parameters: week_number
11. To mark your penalty as done use /finished_penalty
12. to mention this week's users who received a yellow/red card this week use /mention_penalized_users
13. to mention subscribed users use /mention_subscribers (does not mention banned users)
14. to get subscriber's penalty history use /penalty_history
15. [Server Admin Only] To allow kicks in your server use /allow_kicks (You still have to grant the bot permissions to kick members)
16. [Server Admin Only] To disallow kicks in your server use /disallow_kicks
17. [Server Admin Only] to change reminder channel use /set_reminder_channel (by default reminder channel is the server default channel) (use this by going to the channel u want to set and use this command)
18. [Server Admin Only] to reset reminder channel to server default user /reset_reminder_channel
19. [Server Admin Only] to unban a user to be able to use the bot again use /unban_user, Parameters: who
**Rules:**
• Week starts & Reminders ==> Friday 00:00
• Penalties ==> Sunday 00:00
• You get a penalty in 3 conditions (yellow then red):
------>1. you did not complete enough tasks to pass the threshold percentage you registered with
------>2. you did not write your tasks on time
------>3. you did not complete your previous penalty (You have to mark it as done)
• you get a red card if you have 1 penalty previous week and you recieved a new one
• Warning: getting a red card would ban you from using the bot
• You get kicked once getting a red card if the server allows kicks from the bot
    '''
    embed = discord.Embed(title=f'Instructions and Rules',
                              description=info,
                              color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)