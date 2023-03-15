"""A cog that handles errors from app commands globally.

We use this cog to handle errors from app commands globally.
This is to actually handle and respond to errors.
It's nice to not leave the user confused.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlus(...)
    await bot_instance.load_extension("tickets_plus.cogs.errors")
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets Plus Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import discord
from discord import app_commands
from discord.ext import commands

from tickets_plus import bot


class ErrorHandling(commands.Cog, name="AppCommandErrorHandler"):
    """Error handling for Tickets+.

    This cog is used to handle errors from app commands globally.
    This is to actually handle and respond to errors.

    Attributes:
        old_error_handler: The old error handler.
            This is used to restore the old error handler.
    """

    def __init__(self, bot_instance: bot.TicketsPlus) -> None:
        """Initialises the cog instance.

        Args:
            bot_instance: The bot instance.
        """
        self._bt = bot_instance
        self.old_error_handler = None

    async def cog_load(self) -> None:
        """Adds the error handler to the bot.

        Should not be called manually.
        """
        # TODO: Implement this function.
        pass

    async def cog_unload(self) -> None:
        """Removes the error handler from the bot.

        Should not be called manually.
        """
        # TODO: Implement this function.
        pass

    async def on_app_command_error(self, interaction: discord.Interaction,
                                   error: app_commands.AppCommandError) -> None:
        """Handles errors from app commands globally.

        This function is automatically called when an error is raised,
        from an app command.
        This is used to handle and respond to errors.
        So as to not leave the user confused.

        Args:
            interaction: The interaction that raised the error.
            error: The error that was raised.
        """
        # TODO: Implement this function.


async def setup(bot_instance: bot.TicketsPlus) -> None:
    """Sets up the error handler.

    This function is called when the cog is loaded.
    It is used to add the cog to the bot.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(ErrorHandling(bot_instance))
