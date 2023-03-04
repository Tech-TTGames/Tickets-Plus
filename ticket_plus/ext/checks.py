"""Additional checks for bot."""

import discord
from discord.ext import commands

from ticket_plus.database.statvars import Config


def is_owner_gen(confg: Config = Config('offline')):
    """An actually acceptabe way to work around the lack of owner check in slash commands."""

    async def is_owner(interaction: discord.Interaction):
        """Checks if interaction user is owner."""
        if interaction.user.id in confg.owner:
            return True
        await interaction.response.send_message("Error 403: Forbidden", ephemeral=True)
        return False

    return is_owner

def setup(bot: commands.Bot):
    """Set up the extension."""
    cnfg = getattr(bot, "config", Config('offline'))
    check = is_owner_gen(cnfg)
    setattr(bot, "is_owner", check)
