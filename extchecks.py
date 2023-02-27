"""Additional checks for bot."""

import discord

from variables import Config

CONFG = Config('offline')

def is_owner(interaction: discord.Interaction):
    """Checks if interaction user is owner."""
    return interaction.user.id in CONFG.owner
