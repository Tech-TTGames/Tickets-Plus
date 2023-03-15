"""General powertools for the bot owner.

This submodule contains general powertools for the bot owner.
This includes commands to reload cogs, restart the bot, and pull from git.
The last command is to be used very carefully, as changes to the database
schema will require a database migration.

Typical usage example:
    ```py
    from tickets_plus import bot

    await bot.load_extension("tickets_plus.cogs.override")
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets Plus Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from tickets_plus import bot, cogs
from tickets_plus.database import statvars
from tickets_plus.ext import checks

_CNFG = statvars.MiniConfig()
"""Submodule global constant for the config."""


@app_commands.guilds(_CNFG.getitem("dev_guild_id"))
class Overrides(commands.GroupCog,
                name="override",
                description="Owner override commands."):
    """Owner override commands.

    This class contains commands that are only available to the bot owner.
    These commands are used to reload cogs, restart the bot, and pull from git.
    The commands are only available in the development guild.
    """

    def __init__(self, bot_instance: bot.TicketsPlus):
        """Initialises the cog.

        We load the cog here.
        We set the bot instance as an private attribute.
        We then call the super class's __init__ method.

        Args:
            bot_instance: The bot instance.
        """
        self._bt = bot_instance
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="reload", description="Reloads the bot's cogs.")
    @checks.is_owner_check()
    @app_commands.describe(sync="Syncs the tree after reloading cogs.")
    async def reload(self, ctx: discord.Interaction, sync: bool = False):
        """Reloads the bot's cogs.

        This command reloads all cogs in the EXTENSIONS list.
        Reloads are atomic, so if one fails, it rolls back.
        We can just import this submodule and iterate over the EXTENSIONS list.
        You can also sync the tree after reloading cogs. Though this is not
        to be used very often, as it has low rate limits.

        Args:
            ctx: The interaction context.
            sync: Whether to sync the tree after reloading cogs.
        """
        await ctx.response.send_message("Reloading cogs...")
        logging.info("Reloading cogs...")
        for extension in cogs.EXTENSIONS:
            await self._bt.reload_extension(extension)
        await ctx.followup.send("Reloaded cogs.")
        logging.info("Finished reloading cogs.")
        if sync:
            await self._bt.tree.sync()
            logging.info("Finished syncing tree.")

    @app_commands.command(name="close", description="Closes the bot.")
    @checks.is_owner_check()
    async def close(self, ctx: discord.Interaction):
        """Closes the bot.

        If used with a process manager, this will restart the bot.
        This is a bit of a hack, but it works.
        Don't really know how to do this better.

        Args:
            ctx: The interaction context.
        """
        await ctx.response.send_message("Restarting...")
        logging.info("Restarting...")
        await self._bt.close()

    @app_commands.command(
        name="pull", description="Pulls the latest changes from the git repo.")
    @checks.is_owner_check()
    async def pull(self, ctx: discord.Interaction):
        """Pulls the latest changes from the git repo.

        This command pulls the latest changes from the git repo.
        This is a dangerous command, as it can break the bot.
        If you are not sure what you are doing, don't use this command.

        Args:
            ctx: The interaction context.
        """
        await ctx.response.send_message("Pulling latest changes...")
        logging.info("Pulling latest changes...")
        pull = await asyncio.create_subprocess_shell(
            "git pull",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=statvars.PROG_DIR,
        )
        stdo, stdr = await pull.communicate()
        if stdo:
            await ctx.followup.send(f"[stdout]\n{stdo.decode()}")
            logging.info("[stdout]\n%s", stdo.decode())

        if stdr:
            await ctx.followup.send(f"[stderr]\n{stdr.decode()}")
            logging.info("[stderr]\n%s", stdr.decode())

        await ctx.followup.send("Finished pulling latest changes.\n"
                                "Restart bot or reload cogs to apply changes.")

    @app_commands.command(name="logs", description="Sends the logs.")
    @checks.is_owner_check()
    @app_commands.describe(id_no="Log ID (0 for latest log)")
    async def logs(self, ctx: discord.Interaction, id_no: int = 0):
        """Sends the logs.

        This command sends the logs to the user who invoked the command.
        The logs are sent as a file attachment.
        It is possible to specify a log ID, which will send a specific log.
        If no log ID is specified, the latest log will be sent.

        Args:
            ctx: The interaction context.
            id_no: The log ID.
        """
        await ctx.response.defer(thinking=True)
        logging.info("Sending logs to %s...", str(ctx.user))
        filename = f"discord.log{'.'+str(id_no) if id_no else ''}"
        file_path = os.path.join(statvars.PROG_DIR, "log", filename)
        try:
            await ctx.user.send(file=discord.File(fp=file_path))
        except FileNotFoundError:
            await ctx.followup.send("Specified log not found.")
            logging.info("Specified log not found.")
            return
        await ctx.followup.send("Sent logs.")
        logging.info("Logs sent.")

    @app_commands.command(name="config", description="Sends the guild config.")
    @checks.is_owner_check()
    @app_commands.describe(guid="Guild ID")
    async def config(self, ctx: discord.Interaction, guid: int):
        """Sends the config.

        This command sends the config to the user who invoked the command.
        I don't really know if it works with the new db system.
        It is required to specify a guild ID. This is because the config
        is guild specific.

        Args:
            ctx: The interaction context.
            guid: The guild ID.
        """
        await ctx.response.defer(thinking=True)
        logging.info("Sending config to %s...", str(ctx.user))
        async with self._bt.get_connection() as conn:
            guild_confg = await conn.get_guild(guid)
            await ctx.user.send(str(guild_confg)
                               )  # Eh. This is a bit of a test.
        await ctx.followup.send("Sent config.")
        logging.info("Config sent.")

    @commands.command(name="sync", description="Syncs the tree.")
    @checks.is_owner_check()
    async def sync(self, ctx: commands.Context):
        """Syncs the tree.

        This command syncs the tree.
        It is not recommended to use this command often, as it has low rate
        limits. It is the only non-slash command in this bot.

        Args:
            ctx: The command context.
        """
        await ctx.send("Syncing...")
        logging.info("Syncing...")
        await self._bt.tree.sync()
        await ctx.send("Synced.")
        logging.info("Synced.")


async def setup(bot_instance: bot.TicketsPlus):
    """Sets up the overrides.

    We add the overrides to the bot.

    Args:
        bot_instance: The bot.
    """
    await bot_instance.add_cog(Overrides(bot_instance))
