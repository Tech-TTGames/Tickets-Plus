"""Tasks that run in the background from time to time.

This is where the bot's background tasks are defined. These tasks are
scheduled to run at a specific interval, and are generally used to
perform some sort of maintenance or cleanup. Like cleaning up users
who are no longer prevented from something.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlusBot(...)
    bot_instance.load_extension("tickets_plus.cogs.routines")
    ```
"""
from discord.ext import tasks, commands

from tickets_plus import bot


class Routines(commands.Cog):
    """Magic cog for background tasks.

    We do the *real* magic here. This is where the background tasks
    are defined. These tasks are scheduled to run at a specific
    interval, and are generally used to perform some sort of
    maintenance or cleanup.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot):
        """Initialize the cog.

        This is called when the cog is loaded, and initializes the
        background tasks.

        Args:
            bot_instance: The bot instance that loaded the cog.
        """
        self._bt = bot_instance
        self.clean_status.start()

    async def cog_unload(self):
        """Cancel all tasks when the cog is unloaded.

        This is called when the cog is unloaded, and cancels all
        tasks that are running.
        """
        self.clean_status.cancel()

    @tasks.loop(minutes=1)
    async def clean_status(self):
        """Remove all status roles from users whose status has expired.
        
        This task runs every minute, and checks if any users have a
        status role that has expired. If so, it removes the role from
        the user.
        """
        async with self._bt.get_connection() as conn:
            rehabilitated = await conn.get_expired_members()
            for member in rehabilitated:
                gld = member.guild
                usr_id = member.user_id
                actv_guild = self._bt.get_guild(gld.guild_id)
                if actv_guild is None:
                    continue
                actv_member = actv_guild.get_member(usr_id)
                if actv_member is None:
                    continue
                rles = []
                if gld.helping_block:
                    rles.append(actv_guild.get_role(gld.helping_block))
                if gld.support_block:
                    rles.append(actv_guild.get_role(gld.support_block))
                await actv_member.remove_roles(*rles, reason="Status expired")
                member.status = 0
                member.status_till = None
            await conn.commit()

    @clean_status.before_loop
    async def before_clean_status(self):
        """Delay the first run till the bot is ready.

        Ensures that the bot is ready before the first run of the
        task.
        """
        await self._bt.wait_until_ready()


async def setup(bot_instance: bot.TicketsPlusBot):
    """Load the cog into the bot.

    This is called when the cog is loaded, and initializes the
    cog instance.

    Args:
        bot_instance: The bot instance that loaded the cog.
    """
    await bot_instance.add_cog(Routines(bot_instance))