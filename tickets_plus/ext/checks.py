"""Additional checks for bot."""

import discord
from discord import app_commands
from sqlalchemy.orm import selectinload

from tickets_plus.database.models import Guild


def is_owner_check():
    """Now a normal check for owner."""

    async def is_owner(interaction: discord.Interaction):
        """Checks if interaction user is owner."""
        if interaction.user.id in interaction.client.owner_ids:  # type: ignore
            return True
        await interaction.response.send_message("Error 403: Forbidden", ephemeral=True)
        raise app_commands.CheckFailure("User is not owner")

    return app_commands.check(is_owner)


def is_staff_check():
    """An actually normal check for staff."""

    async def is_staff(interaction: discord.Interaction):
        """Checks if interaction user is staff."""
        if interaction.guild is None:
            raise app_commands.CheckFailure("User is not in a guild")
        if interaction.user.id in interaction.client.owner_ids:  # type: ignore
            return True
        async with interaction.client.get_connection() as conn:  # type: ignore
            guild: Guild = await conn.get_guild(
                interaction.guild.id, (selectinload(Guild.staff_roles),)
            )
            staff_roles = guild.get_id_list("staff_roles", "role_id")
            for role in interaction.user.roles:  # type: ignore # already checked for guild
                if role.id in staff_roles:
                    return True
        await interaction.response.send_message("Error 403: Forbidden", ephemeral=True)
        raise app_commands.CheckFailure("User is not staff")

    return app_commands.check(is_staff)
