"""Tickets Plus - A Discord bot for extending Tickets.

This file is the main file for the bot.
It contains the startup code for the bot.
Other code is in the various submodules.
This file is to be used as a module, not as a script.

Typical usage example:
    ```py
    #!/usr/bin/env python3
    import asyncio
    import tickets_plus
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tickets_plus.start_bot(config))
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
import sqlalchemy
from discord.ext import commands
from sqlalchemy.ext import asyncio as sa_asyncio
# Future Proofing for possible future use of asyncio

from tickets_plus import bot
from tickets_plus.database import models, statvars


async def start_bot(stat_data: statvars.MiniConfig = statvars.MiniConfig()):
    """Sets up the bot and starts it. Corutine.

    This function uses the exitsting .json files to set up the bot.
    It also sets up logging, and starts the bot.

    Args:
        stat_data: The statvars.MiniConfig object to use for the bot.
            If None, a new one will be created.
    """

    # Set up logging
    dt_fmr = "%Y-%m-%d %H:%M:%S"
    statvars.HANDLER.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s",
                          dt_fmr))

    # Set up discord.py logging
    dscrd_logger = logging.getLogger("discord")
    dscrd_logger.setLevel(logging.INFO)
    dscrd_logger.addHandler(statvars.HANDLER)

    # Set up sqlalchemy logging
    sql_logger = logging.getLogger("sqlalchemy.engine")
    sql_logger.setLevel(logging.WARNING)
    sql_logger.addHandler(statvars.HANDLER)

    sql_pool_logger = logging.getLogger("sqlalchemy.pool")
    sql_pool_logger.setLevel(logging.WARNING)
    sql_pool_logger.addHandler(statvars.HANDLER)

    # Set up bot logging
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(statvars.HANDLER)
    logging.info("Logging set up.")

    # Set up bot
    logging.info("Creating engine...")
    if "asyncpg" in stat_data.getitem("dbtype"):
        engine = sa_asyncio.create_async_engine(
            stat_data.get_url(),
            pool_size=10,
            max_overflow=-1,
            pool_recycle=600,
            connect_args={"server_settings": {
                "jit": "off"
            }})
    else:
        engine = sa_asyncio.create_async_engine(
            stat_data.get_url(),
            pool_size=10,
            max_overflow=-1,
            pool_recycle=600,
        )
    bot_instance = bot.TicketsPlus(
        db_engine=engine,
        intents=statvars.INTENTS,
        command_prefix=commands.when_mentioned,
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.playing,
                                  name="with tickets"),
    )
    logging.info("Engine created. Ensuring tables...")
    async with engine.begin() as conn:
        await conn.execute(
            sqlalchemy.schema.CreateSchema("tickets_plus", if_not_exists=True))
        await conn.run_sync(models.Base.metadata.create_all)
    logging.info("Tables ensured. Starting bot...")
    try:
        await bot_instance.start(statvars.Secret().token)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Shutting down...")
        # We print this because there was a keyboard interrupt.
        print("Keyboard interrupt detected. Shutting down...")
        await bot_instance.close()
    except SystemExit as exc:
        logging.info("System exit code: %s detected. Closing bot...", exc.code)
        await bot_instance.close()
    else:
        logging.info("Bot shutdown gracefully.")
    logging.info("Bot shutdown complete.")
