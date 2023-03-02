"""Additional checks for bot."""

import discord

from variables import Config

CONFG = Config("offline")

def is_owner_gen(confg: Config = CONFG):
    async def is_owner(interaction: discord.Interaction):
        """Checks if interaction user is owner."""
        if interaction.user.id in confg.owner:
            return True
        await interaction.response.send_message("Error 400: Forbidden", ephemeral=True)
        return False
    return is_owner
