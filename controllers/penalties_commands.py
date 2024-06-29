from discord.ext import commands
# from client import kick, reminder
from models.subscriber import Subscriber
from models.task import Task
from models.week import Week
from models.penalty import Penalty
from data_access import penalties_access, weeks_access, subscribers_access, guilds_access
class PenaltiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# TODO: reminders and guild scheduling

    def run_penalties(self, day: int) -> None:
        reminder_guilds, apply_guilds = guilds_access.get_today_guilds(day)
        for guild in reminder_guilds:
            self.weekly_check(guild.guild_id, True)
        for guild in apply_guilds:
            self.weekly_check(guild.guild_id, False)


    def weekly_check(self, guild_id, remind: bool) -> None:
        week_num = weeks_access.get_current_week()
        # get all users having this guild_id and not is_banned in a list of ids
        subscribers = []
        for subscriber in subscribers:
            previous_card = penalties_access.get_subscriber_penalty_history(subscriber=subscriber)
            if previous_card:
                previous_card = previous_card[-1]
            else:
                previous_card = None
            card = self.check_user(subscriber, week_num, previous_card)
            if card:
                if remind:
                    # reminder(subscriber.user_id, guild_id)
                    return
                is_yellow = 1
                desc = subscriber.default_yellow_penalty_description
                if previous_card:
                    # red card
                    is_yellow = 0
                    # kick(subscriber.user_id, guild_id)
                    desc = subscriber.default_red_penalty_description
                    subscribers_access.ban_user(subscriber)
                # add penalty in db
                penalty = Penalty(description=desc, is_yellow=is_yellow, week_number=week_num, guild_id=guild_id, owner_id=subscriber.user_id)
                penalties_access.add_penalty(penalty)


    # checks user weekly progress and returns true if he should recieve a card
    def check_user(self, subscriber: Subscriber, week_num: int, previous_card: Penalty) -> bool:
        if previous_card and not previous_card.is_done:
            return True
        tasks = subscribers_access.get_subscriber_tasks(subscriber, week_num)
        total = len(tasks)
        if not total:
            return True
        completed = 0.0
        for task in tasks:
            completed += task.completion_percentage
        return completed / total < subscriber.threshold



async def setup(bot):
    await bot.add_cog(PenaltiesCog(bot))

def run(day: int):
    penalties = PenaltiesCog()
    print("running penalties")
    penalties.run_penalties(day)