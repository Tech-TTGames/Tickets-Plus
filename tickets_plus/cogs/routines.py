"""Tasks that run in the background from time to time.

This is where the bot's background tasks are defined. These tasks are
scheduled to run at a specific interval, and are generally used to
perform some sort of maintenance or cleanup. Like cleaning up users
who are no longer prevented from something.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlusBot(...)
    await bot_instance.load_extension("tickets_plus.cogs.routines")
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.

from discord.ext import commands, tasks

from tickets_plus import bot
from tickets_plus.database import config

_CNFG = config.RuntimeConfig()


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
        self.notify_users.start()

    async def cog_unload(self):
        """Cancel all tasks when the cog is unloaded.

        This is called when the cog is unloaded, and cancels all
        tasks that are running.
        """
        self.clean_status.cancel()
        self.notify_users.cancel()

    @tasks.loop(seconds=_CNFG.spt_clean_usr)
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

    @tasks.loop(seconds=_CNFG.spt_notif_usr)
    async def notify_users(self):
        """Notifies users of their tickets closing soon.

        Running every 2 minutes and 30 seconds, this task checks if
        any tickets are lacking responses,
        (time since last message above warning threshold)
        and if so, sends a warning message to the user.
        """
        async with self._bt.get_connection() as conn:
            tickets = await conn.get_pending_tickets()
            for ticket in tickets:
                ticket.notified = True
                gld = ticket.guild
                usr_id = ticket.user_id
                if usr_id is None:
                    continue
                actv_guild = self._bt.get_guild(gld.guild_id)
                if actv_guild is None:
                    continue
                actv_member = actv_guild.get_member(usr_id)
                if actv_member is None:
                    continue
                appnd = "Please respond soon, or it will be closed."
                if gld.any_autoclose:
                    appnd = (
                        "Please respond soon, or it will be closed "
                        # pylint: disable=line-too-long # skipcq: FLK-E501
                        f"<t:{int((ticket.last_response + gld.any_autoclose).timestamp())}:R>."
                    )
                txt = (
                    f"Your ticket <#{ticket.channel_id}> in {actv_guild.name} "
                    f"is still open. {appnd}")
                await actv_member.send(txt)
            await conn.commit()

    @notify_users.before_loop
    async def before_notify_users(self):
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
