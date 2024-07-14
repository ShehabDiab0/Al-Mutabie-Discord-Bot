# ------------------------ Scheduling functions/commands ------------------------
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


async def run_scheduler():
    scheduler.start()
    scheduler.add_job(weeks_access.add_week, trigger='cron', day_of_week=DAY_TO_RESET, timezone=TIMEZONE)
    # scheduler.add_job(weeks_access.add_week, trigger='cron',second='*', timezone=TIMEZONE)
    #print all the jobs
    print("Scheduler started")

@bot.tree.command(name="pause_scheduler")
@app_commands.checks.has_permissions(administrator=True)
@commands.guild_only()
async def pause_scheduler(interaction: discord.Interaction):
    scheduler.pause()
    await interaction.response.send_message("Scheduler paused")

@bot.tree.command(name="resume_scheduler")
@app_commands.checks.has_permissions(administrator=True)
@commands.guild_only()
async def resume_scheduler(interaction: discord.Interaction):
    scheduler.resume()
    await interaction.response.send_message("Scheduler resumed")


@pause_scheduler.error
@resume_scheduler.error
async def scheduler_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permissions to use this command.", ephemeral=True)
