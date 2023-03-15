"""Settings change commands for Tickets+.

This extension provides commands to change the bot's settings.
Those settings are guild-specific and are stored in the database.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlusBot(...)
    await bot_instance.load_extension("tickets_plus.cogs.settings")
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
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

from tickets_plus import bot


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Settings(commands.GroupCog,
               name="settings",
               description="Settings for the bot."):
    """Provides commands to change the bot's settings.

    These settings are guild-specific and are stored in the database.
    We suggest the settings to be only changed by administrators,
    however this can be changed discord-side.
    This is a group cog, so all commands are under the settings group.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot):
        """Initialises the cog.

        We initialise the variables we need.
        Then we call the super class's __init__ method.

        Args:
            bot: The bot instance.
        """
        self._bt = bot_instance
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="ticketbot",
                          description="Change the ticket bots for your server.")
    @app_commands.describe(user="The user to add to ticket bots.")
    async def change_tracked(self, ctx: discord.Interaction,
                             user: discord.User):
        """Changes the tickets bot for the server.

        This command is used to change the ticket bots users.
        Ticket bots are users that can create tickets to be handled by our bot.

        Args:
            ctx: The interaction context.
            user: The user to add/remove to ticket bots.
        """
        async with self._bt.get_connection() as conn:
            new, ticket_user = await conn.get_ticket_bot(
                user.id,
                ctx.guild.id,  # type: ignore
            )
            if not new:
                await conn.delete(ticket_user)
                text = f"Untracked {user.mention}"
            else:
                text = f"Tracked {user.mention}"
            await conn.commit()
        await ctx.response.send_message(text, ephemeral=True)

    @app_commands.command(name="staff", description="Change the staff roles.")
    @app_commands.describe(role="The role to add/remove from staff roles.")
    async def change_staff(self, ctx: discord.Interaction, role: discord.Role):
        """Changes the staff roles for the server.

        This command is used to change the staff roles.
        Staff roles are roles that can use the staff commands.
        I mean, it's pretty obvious, isn't it?

        Args:
            ctx: The interaction context.
            role: The role to add/remove from staff roles.
        """
        async with self._bt.get_connection() as conn:
            new, staff_role = await conn.get_staff_role(
                role.id,
                ctx.guild.id,  # type: ignore
            )
            if not new:
                await conn.delete(staff_role)
                text = f"Removed {role.mention} from staff roles."
            else:
                text = f"Added {role.mention} to staff roles."
            await conn.commit()
        await ctx.response.send_message(text, ephemeral=True)

    @app_commands.command(name="observers",
                          description="Change the observers roles.")
    @app_commands.describe(role="The role to add/remove from observers roles.")
    async def change_observers(self, ctx: discord.Interaction,
                               role: discord.Role):
        """Changes the observers roles for the server.

        This command is used to change the observers roles.
        Observers roles are roles that are automatically added to ticket notes.
        They are to be used in conjunction with the staff roles.
        As observers don't have access to staff commands.

        Args:
            ctx: The interaction context.
            role: The role to add/remove from observers roles.
        """
        async with self._bt.get_connection() as conn:
            new, obsrvrs = await conn.get_observers_role(
                role.id,
                ctx.guild.id,  # type: ignore
            )
            if not new:
                await conn.delete(obsrvrs)
                text = f"Removed {role.mention} from ping staff roles."
            else:
                text = f"Added {role.mention} to ping staff roles."
            await conn.commit()
        await ctx.response.send_message(text, ephemeral=True)

    @app_commands.command(name="communitysupport",
                          description="Change the community support roles.")
    @app_commands.describe(
        role="The role to add/remove from community support roles.")
    async def change_community_roles(self, ctx: discord.Interaction,
                                     role: discord.Role):
        """Modifies the server's community support roles.

        This command is used to change the community support roles.
        Community support roles are roles that are automatically added to
        community support tickets. But do not recive any permissions.
        They are not pinged when a new ticket is created.

        Args:
            ctx: The interaction context.
            role: The role to add/remove from community support roles.
        """
        async with self._bt.get_connection() as conn:
            new, comsup = await conn.get_community_role(
                role.id,
                ctx.guild.id,  # type: ignore
            )
            if not new:
                await conn.delete(comsup)
                text = f"Removed {role.mention} from community support roles."
            else:
                text = f"Added {role.mention} to community support roles."
            await conn.commit()
        await ctx.response.send_message(text, ephemeral=True)

    @app_commands.command(name="communityping",
                          description="Change the community ping roles.")
    @app_commands.describe(
        role="The role to add/remove from community ping roles.")
    async def change_community_ping_roles(self, ctx: discord.Interaction,
                                          role: discord.Role):
        """Modifies the server's community ping roles.

        This command is used to change the community ping roles.
        Community ping roles are to be used in conjunction with the community
        support roles. They are pinged when a new ticket is created but,
        after the addition of the community support roles.
        They are not given any permissions, including the ability to see the
        tickets. They are only pinged.

        Args:
            ctx: The interaction context.
            role: The role to add/remove from community ping roles.
        """
        async with self._bt.get_connection() as conn:
            new, comsup = await conn.get_community_ping(
                role.id,
                ctx.guild.id,  # type: ignore
            )
            if not new:
                await conn.delete(comsup)
                text = f"Removed {role.mention} from community ping roles."
            else:
                text = f"Added {role.mention} to community ping roles."
            await conn.commit()
        await ctx.response.send_message(text, ephemeral=True)

    @app_commands.command(name="openmsg",
                          description="Change the open message.")
    @app_commands.describe(message="The new open message.")
    async def change_openmsg(self, ctx: discord.Interaction, message: str):
        """This command is used to change the open message.

        This is the message that opens a new ticket notes thread.
        It is only visible to the staff team and observers.
        The message must be less than 200 characters.
        The default message is "Staff notes for Ticket $channel".
        Where $channel is the channel mention.

        Args:
            ctx: The interaction context.
            message: The new open message.

        Raises:
            app_commands.AppCommandError: The message is too long.
        """
        if len(message) > 200:
            raise app_commands.AppCommandError("The message must be less than"
                                               " 200 characters.")
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            guild.open_message = message
            await conn.commit()
        await ctx.response.send_message(f"Open message is now {message}",
                                        ephemeral=True)

    @app_commands.command(name="staffteamname",
                          description="Change the staff team's name.")
    @app_commands.describe(name="The new staff team's name.")
    async def change_staffteamname(self, ctx: discord.Interaction, name: str):
        """This command is used to change the staff team's name.

        We use this name when the bot sends messages as the staff team.
        So it is important that it is set to something that makes sense.
        The default is "Staff Team". But you can change it to whatever you
        want. It is limited to 40 characters.

        Args:
            ctx: The interaction context.
            name: The new staff team's name.

        Raises:
            app_commands.AppCommandError: The name is too long.
        """
        if len(name) > 40:
            await ctx.response.send_message(
                "The name must be less than 40 characters.", ephemeral=True)
            raise app_commands.AppCommandError("Name too long")
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            guild.staff_team_name = name
            await conn.commit()
        await ctx.response.send_message(f"Staff team is now {name}",
                                        ephemeral=True)

    @app_commands.command(name="autoclose",
                          description="Change the autoclose time.")
    @app_commands.describe(
        days="The new autoclose time days.",
        hours="The new autoclose time hours.",
        minutes="The new autoclose time minutes.",
    )
    async def change_autoclose(self,
                               ctx: discord.Interaction,
                               days: int = 0,
                               hours: int = 0,
                               minutes: int = 0):
        """Set the guild-wide autoclose time.

        This command is used to change the autoclose time.
        We use this time to correctly calculate the time until a ticket
        is automatically closed. This is the time that is displayed
        in the ticket's description. Additionally, this is the time
        we may later use to warn the user that their ticket is about
        to be closed.

        Args:
            ctx: The interaction context.
            days: The new autoclose time days. Defaults to 0.
            hours: The new autoclose time hours. Defaults to 0.
            minutes: The new autoclose time minutes. Defaults to 0.
        """
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            if days + hours + minutes == 0:
                guild.first_autoclose = None
                text = "Autoclose disabled."
            else:
                guild.first_autoclose = int(
                    timedelta(days=days, hours=hours,
                              minutes=minutes).total_seconds() / 60)
                text = f"Autoclose set to {guild.first_autoclose} minutes."
            await conn.commit()
        await ctx.response.send_message(text, ephemeral=True)

    @app_commands.command(name="msgdiscovery",
                          description="Toggle message link discovery.")
    async def toggle_msg_discovery(self, ctx: discord.Interaction):
        """This command is used to toggle message link discovery.

        This is the feature that makes the bot automatically
        resolve message links to their content and reply with
        the content of the message. This is useful for staff
        to quickly see what a user is referring to.

        Args:
            ctx: The interaction context.
        """
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            new_status = not guild.msg_discovery
            guild.msg_discovery = new_status
            await conn.commit()
        await ctx.response.send_message(
            f"Message link discovery is now {new_status}",
            ephemeral=True,
        )

    @app_commands.command(name="stripbuttons",
                          description="Toggle button stripping.")
    async def toggle_button_stripping(self, ctx: discord.Interaction):
        """This command is used to toggle button stripping.

        Button stripping is the feature that makes the bot
        remove buttons from messages that are sent by the
        ticket bots. This is useful for cleaning up the
        ticket channel. Additionally, we may later use this
        to filter out content from the ticket information.

        Args:
            ctx: The interaction context.
        """
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            new_status = not guild.strip_buttons
            guild.strip_buttons = new_status
            await conn.commit()
        await ctx.response.send_message(
            f"Button stripping is now {new_status}",
            ephemeral=True,
        )


async def setup(bot_instance: bot.TicketsPlusBot):
    """Setup up the settings commands.
    
    We add the settings cog to the bot.
    Nothing different from the normal setup function.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(Settings(bot_instance))
