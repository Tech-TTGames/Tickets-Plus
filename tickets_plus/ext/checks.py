"""Additional checks for bot."""

import discord
from discord import app_commands


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
            staff_roles = await conn.get_all_staff_roles(interaction.guild.id)
            for role in staff_roles:
                parsed_role = interaction.guild.get_role(role.role_id)
                if parsed_role in interaction.user.roles:  # type: ignore
                    # Alredy checked for member
                    return True
        await interaction.response.send_message("Error 403: Forbidden", ephemeral=True)
        raise app_commands.CheckFailure("User is not staff")

    return app_commands.check(is_staff)
