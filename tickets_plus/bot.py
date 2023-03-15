"""This main bot class module for Tickets Plus.

A module that contains purely the bot class.
It's a subclass of discord.ext.commands.AutoShardedBot.
No other code is in this module at the moment.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlus(...)
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets Plus Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import logging

import discord
from discord.ext import commands
from sqlalchemy.ext import asyncio as sa_asyncio
# Future Proofing for possible future use of asyncio

from tickets_plus import cogs
from tickets_plus.database import layer, statvars


class TicketsPlus(commands.AutoShardedBot):
    """A bot instance that is used to run Tickets Plus.

    A bot instance that is used to run Tickets Plus.
    This is to allow us to add our own methods and attributes.
    In general, not much is done in this class.
    Most of the work is done in the cogs.

    Attributes:
        stat_confg (statvars.MiniConfig): The config for the bot.
        sessions (sqlalchemy_asyncio.async_sessionmaker):
            The database session maker.
    """

    def __init__(self,
                 *args,
                 db_engine: sa_asyncio.AsyncEngine,
                 confg: statvars.MiniConfig = statvars.MiniConfig(),
                 **kwargs) -> None:
        """Initialises the bot instance.

        Args:
            *args: The arguments to pass to the super class.
            db_engine: The database engine.
            confg: The config for the bot.
                Defaults to statvars.MiniConfig().
            **kwargs: The keyword arguments to pass to the super class.
        """
        super().__init__(*args, **kwargs)
        self._db_engine = db_engine
        self.stat_confg = confg
        self.sessions = sa_asyncio.async_sessionmaker(self._db_engine,
                                                      expire_on_commit=False)

    async def setup_hook(self) -> None:
        """Runs just before the bot connects to Discord.

        This function is called just before the bot connects to Discord.
        This is used to load the cogs and sync the database.
        Generally, this function should not be called manually.
        """
        logging.info("Bot version: %s", statvars.VERSION)
        logging.info("Discord.py version: %s", discord.__version__)
        logging.info("Loading cogs...")
        for extension in cogs.EXTENSIONS:
            try:
                await self.load_extension(extension)
            except commands.ExtensionError as err:
                logging.error("Failed to load cog %s: %s", extension, err)
        logging.info("Finished loading cogs.")
        if self.stat_confg.getitem("dev_guild_id"):
            guild = discord.Object(self.stat_confg.getitem("dev_guild_id"))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    def get_connection(self) -> layer.OnlineConfig:
        """Gets a connection from the database pool.

        This function is used to get a connection from the database pool.
        We additionally wrap the connection in a OnlineConfig object.
        This is to allow us to use the OnlineConfig object as a context manager.
        And to allow for more convenient access to the database.

        Returns:
            layer.OnlineConfig: The OnlineConfig object.
                A wrapper for the database connection.
        """
        return layer.OnlineConfig(self, self.sessions())

    async def close(self) -> None:
        """Closes the bot.

        This function is used to close the bot.
        We additionally close the database engine.
        """
        logging.info("Closing bot...")
        await self._db_engine.dispose()
        return await super().close()
