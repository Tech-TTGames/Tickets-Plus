"""A cog that handles errors from app commands globally.

We use this cog to handle errors from app commands globally.
This is to actually handle and respond to errors.

Example:
    ```py
    from tickets_plus import bot
    bot = bot.TicketsPlus(...)
    await bot.load_extension("tickets_plus.cogs.errors")
    ```
"""
# License: EPL-2.0
# Copyright (c) 2021-2023 The Tickets Plus Contributors
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands

from tickets_plus import bot


class ErrorHandling(commands.Cog, name="AppCommandErrorHandler"):
    """A cog that handles errors from app commands globally.

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
              A bot.TicketsPlus instance.
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

    async def on_app_command_error(self, interaction: Interaction,
                                   error: AppCommandError) -> None:
        """Handles errors from app commands globally.

        This function is automatically called when an error is raised,
        from an app command.
        This is used to handle and respond to errors.
        So as to not leave the user confused.

        Args:
            interaction (Interaction): The interaction that raised the error.
            error (AppCommandError): The error that was raised.
        """
        # TODO: Implement this function.


async def setup(bot_instance: bot.TicketsPlus) -> None:
    """Adds the cog to the bot.

    Args:
        bot_instance: The bot instance.
          A bot.TicketsPlus instance.
    """
    await bot_instance.add_cog(ErrorHandling(bot_instance))
