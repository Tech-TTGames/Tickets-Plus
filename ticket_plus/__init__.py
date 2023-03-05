"""The main bot file. Start the bot."""
import logging

import discord
from discord.ext import commands

from ticket_plus.cogs import EXTENSIONS
from ticket_plus.database.statvars import VERSION, Secret, handler, intents


class TicketPlus(commands.AutoShardedBot):
    """The main bot class"""
    def __init__(self, *args, db_engine, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_engine = db_engine

    async def setup_hook(self):
        """Runs just before the bot connects to Discord"""

        logging.info("Bot version: %s", VERSION)
        logging.info("Discord.py version: %s", discord.__version__)
        logging.info("Loading checks...")
        await self.load_extension("ticket_plus.ext.checks")
        logging.info("Loading cogs...")
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
            except commands.ExtensionError as err:
                logging.error("Failed to load cog %s: %s", extension, err)


async def start_bot():
    """Sets up the bot and starts it"""

    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    dt_fmr = "%Y-%m-%d %H:%M:%S"
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s", dt_fmr)
    )
    logger.addHandler(handler)
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(handler)

    logging.info("Starting bot...")
    # async with
