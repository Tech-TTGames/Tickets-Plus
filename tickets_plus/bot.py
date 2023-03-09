"""The main bot class"""
import logging

import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from tickets_plus.cogs import EXTENSIONS
from tickets_plus.database.layer import OnlineConfig
from tickets_plus.database.statvars import VERSION, MiniConfig


class TicketsPlus(commands.AutoShardedBot):
    """The main bot class"""

    def __init__(
        self, *args, db_engine: AsyncEngine, confg: MiniConfig = MiniConfig(), **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.db_engine: AsyncEngine = db_engine
        self.stat_confg: MiniConfig = confg
        self.sessions = async_sessionmaker(self.db_engine, expire_on_commit=False)

    async def setup_hook(self) -> None:
        """Runs just before the bot connects to Discord"""
        logging.info("Bot version: %s", VERSION)
        logging.info("Discord.py version: %s", discord.__version__)
        logging.info("Loading cogs...")
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
            except commands.ExtensionError as err:
                logging.error("Failed to load cog %s: %s", extension, err)
        logging.info("Finished loading cogs.")
        if self.stat_confg.getitem("dev_guild_id"):
            guild = discord.Object(self.stat_confg.getitem("dev_guild_id"))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    def get_connection(self) -> OnlineConfig:
        """Gets a connection from the database pool"""
        return OnlineConfig(self, self.sessions())

    async def close(self) -> None:
        """Closes the bot"""
        logging.info("Closing bot...")
        await self.db_engine.dispose()
        return await super().close()
