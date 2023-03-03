"""The main bot file. Start the bot."""
import logging
import os

import discord
from discord.ext import commands

from tickbot.database.statvars import (
    PROG_DIR,
    VERSION,
    Config,
    Secret,
    handler,
    intents,
)


def init_bot():
    """Initializes the bot"""
    bot = commands.AutoShardedBot(command_prefix="~", intents=intents)
    scrt = Secret()
    # TODO: Actually use the configdb

    @bot.event
    async def on_ready():
        """Logs bot readiness"""
        logging.info("Connected to Discord as %s", bot.user)
        logging.info("Bot version: %s", VERSION)
        logging.info("Discord.py version: %s", discord.__version__)
        logging.info("Loading cogs...")
        for cog in os.listdir(os.path.join(PROG_DIR, "tickbot", "cogs")):
            try:
                if (
                    cog.endswith(".py")
                    and not cog.startswith("_")
                    and os.path.isfile(cog)
                ):
                    await bot.load_extension(f"tickbot.cogs.{cog[:-3]}")
            except commands.ExtensionError as err:
                logging.error("Failed to load cog %s: %s", cog, err)
        await bot.tree.sync()
        logging.info("Finished loading cogs.")

    bot.run(scrt.token, log_handler=handler, root_logger=True)
