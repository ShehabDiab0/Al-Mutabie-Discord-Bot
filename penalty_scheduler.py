import discord
from discord.ext import commands
from data_access import penalties_access, weeks_access
from data_access.guilds_access import get_channel_id
from data_access import weeks_access, subscribers_access, guilds_access, tasks_access
from models.subscriber import Subscriber
from models.penalty import Penalty
from models.guild import Guild


# reminder for everyone
async def send_reminder(bot, guild_id: str):
    guild_id = int(guild_id)
    guild = bot.get_guild(guild_id)
    user_ids = subscribers_access.get_subscribers(guild_id)
    user_ids = [int(x.user_id) for x in user_ids]
    channel_id = int(get_channel_id(guild_id))
    # Fetch the channel object using the channel ID
    channel = bot.get_channel(channel_id)
    if not (channel and user_ids):
        print("User or channel not found.")
        return

    message = "A new week has started. \nSelf report your last week and add your new tasks.\n You have 2 days\n"
    # Fetch each user object for mentioning using the user ID
    for user_id in user_ids:
        user = guild.get_member(user_id)
        if user:
            message += user.mention
    # Send a message in the channel mentioning the user
    await channel.send(message)


# send card
async def send_card(bot, user_id: str, guild_id: str, penalty: Penalty):
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


@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def kick(bot, user_id: str, guild_id: str):
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

        # Fetch the member
        member = guild.get_member(user_id)
        if not member:
            await channel.send('Member not found.')
            return
        # Kick the member
        await member.kick(reason=reason)
        await channel.send(f'{member.mention} has been kicked for: {reason}')
    except ValueError:
        print('Invalid guild_id, user_id, or channel_id.')
    except discord.Forbidden:
        await channel.send('I do not have permission to kick this user.')
    except discord.HTTPException as e:
        await channel.send(f'Failed to kick the user. Error: {e}')



class Penalties():
    # constructor that takes bot
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def remind_everyone(self) -> None:
        reminder_guilds = guilds_access.get_all_guilds()
        for guild in reminder_guilds:
            self.bot.loop.create_task(send_reminder(self.bot, guild.guild_id))


    def run_penalties(self, day: int) -> None:
        print("running penalties")
        apply_guilds = guilds_access.get_today_guilds(day)
        for guild in apply_guilds:
            self.weekly_check(guild)


    def weekly_check(self, guild: Guild) -> None:
        guild_id = guild.guild_id
        print("weekly check")
        week_num = weeks_access.get_current_week()
        # get all users having this guild_id and not is_banned in a list of ids
        subscribers = subscribers_access.get_subscribers(guild_id)
        for subscriber in subscribers:
            # check if subscriber exists in the discord server
            bot_guild = self.bot.get_guild(int(guild_id)) 
            # check if the bot got kicked or the user left the server
            if bot_guild is None or bot_guild.get_member(int(subscriber.user_id)) is None: 
                continue
            previous_card = penalties_access.get_subscriber_penalty_history(subscriber=subscriber)
            if previous_card:
                previous_card = previous_card[-1]
            else:
                previous_card = None
            card = self.check_user(subscriber, week_num - 1, previous_card)
            if card:
                is_yellow = 1
                desc = subscriber.default_yellow_description
                if previous_card and ((week_num - previous_card.week_number) <= 1):
                    # red card
                    is_yellow = 0
                    if guild.allow_kicks:
                        print('kick')
                        self.bot.loop.create_task(kick(self.bot, subscriber.user_id, guild_id))
                    desc = subscriber.default_red_description
                    subscribers_access.ban_user(subscriber)
                # add penalty in db
                penalty = Penalty(description=desc, is_yellow=is_yellow, week_number=week_num, guild_id=guild_id, owner_id=subscriber.user_id, is_done=False)
                self.bot.loop.create_task(send_card(self.bot, subscriber.user_id, guild_id, penalty))
                penalties_access.add_penalty(penalty)


    # checks user weekly progress and returns true if he should receive a card
    def check_user(self, subscriber: Subscriber, week_num: int, previous_card: Penalty) -> bool:
        # get user start week
        first_week = tasks_access.get_subscriber_first_week(subscriber)
        if week_num < first_week:
            return False
        if previous_card and not previous_card.is_done:
            return True
        tasks = tasks_access.get_subscriber_tasks(subscriber, week_num)
        total = len(tasks)
        if not total:
            return True
        completed = 0.0
        for task in tasks:
            completed += task.completion_percentage
        return completed / total < (subscriber.threshold_percentage)