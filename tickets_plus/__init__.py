"""The main bot file. Start the bot."""
import logging

import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import create_async_engine

from tickets_plus.cogs import EXTENSIONS
from tickets_plus.database.layer import OnlineConfig
from tickets_plus.database.statvars import VERSION, Secret, handler, intents


class TicketsPlus(commands.AutoShardedBot):
    """The main bot class"""

    def __init__(self, *args, db_engine: AsyncEngine, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_engine: AsyncEngine = db_engine
        self.sessions = async_sessionmaker(self.db_engine, expire_on_commit=False)

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

    def get_connection(self):
        """Gets a connection from the database pool"""
        return OnlineConfig(self, self.sessions())

    async def close(self):
        """Closes the bot"""
        logging.info("Closing bot...")
        await self.db_engine.dispose()
        return await super().close()


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

    engine = create_async_engine(stat_data.get_url())
    bot = TicketsPlus(
        db_engine=engine, intents=intents, command_prefix=commands.when_mentioned
    )
    try:
        await bot.start(Secret().token)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Shutting down...")
        # We print this because there was a keyboard interrupt.
        print("Keyboard interrupt detected. Shutting down...")
        await bot.close()
    except SystemExit as exc:
        logging.info("System exit code: %s detected. Closing bot...", exc.code)
        await bot.close()
    else:
        logging.info("Bot shutdown gracefully.")
    logging.info("Bot shutdown complete.")
