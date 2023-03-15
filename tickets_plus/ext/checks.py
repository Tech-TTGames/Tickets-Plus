"""Tickets Plus decorators for use with discord.py app commands.

A set of decorators for use with discord.py application commands.
These are generally Ticket Plus specific checks.
They require the client to be a tickets_plus.bot.TicketsPlus instance.

Typical usage example:
    ```py
    from discord import app_commands
    from tickets_plus.ext import checks

    @app_commands.command()
    @checks.is_owner_check()
    async def command(interaction: discord.Interaction):
        ...
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


def is_owner_check():
    """A check for owner only commands.

    We need to create our own check because the default one doesn't work with
    application commands.

    Returns:
        app_commands.check: The check.
            It's a decorator, so you can use it like this:
            ```py
            @app_commands.command()
            @is_owner_check()
            async def command(interaction: discord.Interaction):
                ...
            ```
    """

    async def is_owner(interaction: discord.Interaction) -> bool:
        """Checks if interaction user is owner.

        The actual check. It's a coroutine, so it can be awaited.

        Args:
            interaction: The interaction to check.

        Returns:
            bool: Whether the user is owner or not.
                Doesn't return if the user is not owner.

        Raises:
            app_commands.CheckFailure: If the user is not owner.
                This is according to the discord.py convention.
        """
        if interaction.user.id in interaction.client.owner_ids:  # type: ignore
            return True
        await interaction.response.send_message("Error 403: Forbidden",
                                                ephemeral=True)
        raise app_commands.CheckFailure("User is not owner")

    return app_commands.check(is_owner)


def is_staff_check():
    """A staff check using the database.

    We need create our own check so we can use the database.

    Returns:
        app_commands.check: The check.
            It's a decorator, so you can use it like this:
            ```py
            @app_commands.command()
            @is_staff_check()
            async def command(interaction: discord.Interaction):
                ...
            ```
    """

    async def is_staff(interaction: discord.Interaction):
        """Checks if interaction user is staff.

        The actual check. It's a coroutine, so it can be awaited.

        Args:
            interaction: The interaction to check.

        Returns:
            bool: Whether the user is staff or not.
                Doesn't return if the user is not staff.

        Raises:
            app_commands.CheckFailure: If the user is not staff.
                This is according to the discord.py convention.
        """
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
        await interaction.response.send_message("Error 403: Forbidden",
                                                ephemeral=True)
        raise app_commands.CheckFailure("User is not staff")

    return app_commands.check(is_staff)
