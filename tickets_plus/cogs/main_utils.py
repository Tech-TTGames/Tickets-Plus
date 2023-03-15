"""Miscellaneous commands that don't fit anywhere else.

This module contains commands that don't fit anywhere else.
They are various commands that don't fit into any other category.
They are in free discord commands not assigned to groups.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlus(...)
    await bot_instance.load_extension("tickets_plus.cogs.main_utils")
    ```
"""
# License: EPL-2.0
# Copyright (c) 2021-present The Tickets Plus Contributors
import logging
import string

import discord
from discord import app_commands, utils
from discord.ext import commands

from tickets_plus import bot
from tickets_plus.database import statvars
from tickets_plus.ext import checks


class FreeCommands(commands.Cog, name="General Random Commands"):
    """General commands that don't fit anywhere else.

    We assign various commands that don't fit anywhere else to this cog.
    They are in free discord commands not assigned to groups.
    If a context is big enough, we may move it to a group.
    """

    def __init__(self, bot_instance: bot.TicketsPlus):
        """Initialise the FreeCommands cog.

        We initialise the cog here.
        We also log that the cog has been loaded correctly.

        Args:
            bot_instance: The bot instance that loaded this cog.
        """
        self._bt = bot_instance
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(
        name="ping",
        description="The classic ping command. Checks the bot's latency.")
    async def ping(self, ctx: discord.Interaction):
        """The classic ping command. Checks the bot's latency.

        This command is used to check the bot's latency.
        It responds with the bot's latency in milliseconds.

        Args:
            ctx: The interaction context.
        """
        await ctx.response.send_message("Pong! The bot is online.\nPing: "
                                        f"{str(round(self._bt.latency * 1000))}"
                                        "ms")

    @app_commands.command(name="version", description="Get the bot's version.")
    async def version(self, ctx: discord.Interaction):
        """This command is used to check the bot's version.

        Responds with the bot's version and a link to the source code.

        Args:
            ctx: The interaction context.
        """
        await ctx.response.send_message(
            f"Bot 'Tickets Plus' version: {statvars.VERSION}"
            " by Tech. TTGames#8616\n"
            "This bot is open source and experimental!\n"
            "Check it out and report issues at:"
            "https://github.com/Tech-TTGames/Tickets-Plus")

    @app_commands.command(name="respond",
                          description="Respond to a ticket as the bot.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    @app_commands.describe(message="The message to send to the ticket.")
    async def respond(self, ctx: discord.Interaction, message: str):
        """Respond to a ticket as the bot.

        This command is used to respond to a ticket as the bot.
        It can be used in a ticket channel or a staff notes thread.
        It then sends the message to the ticket as the bot.

        Args:
            ctx: The interaction context.
            message: The message to send to the ticket.

        Raises:
            AppCommandError: If the channel is neither a ticket, nor thread.
        """
        async with self._bt.get_connection() as confg:
            guild = await confg.get_guild(
                ctx.guild.id)  # type: ignore # checked in decorator
            sanitized_message = utils.escape_mentions(message)
            if isinstance(ctx.channel, discord.Thread):
                ticket = await confg.fetch_ticket(
                    ctx.channel.parent.id  # type: ignore
                )
                if ticket is None:
                    raise app_commands.AppCommandError(
                        "This channel is not a ticket.")
                if ticket.staff_note_thread != ctx.channel.id:
                    raise app_commands.AppCommandError(
                        "This channel is not a staff notes thread.")
                await ctx.response.send_message(
                    f"Responding to ticket with message:\n{sanitized_message}")
                await ctx.channel.parent.send(  # type: ignore
                    f"**{guild.staff_team_name}:** {sanitized_message}")

            elif isinstance(ctx.channel, discord.TextChannel):
                ticket = await confg.fetch_ticket(ctx.channel.id)
                if ticket is None:
                    raise app_commands.AppCommandError(
                        "This channel is not a ticket."
                        " If it is, use /register.")
                await ctx.response.send_message(
                    f"Responding to ticket with message:\n{sanitized_message}",
                    ephemeral=True,
                )
                await ctx.channel.send(
                    f"**{guild.staff_team_name}:** {sanitized_message}")

            await confg.close()

    @app_commands.command(name="join",
                          description="Join a ticket's staff notes.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    async def join(self, ctx: discord.Interaction):
        """Adds the user to the ticket's staff notes thread.

        This command is used to add the user to the ticket's staff notes thread.
        It's used to allow the joining without the need for the user to have
        the Manage Threads permission.

        Args:
            ctx: The interaction context.
        Raises:
            AppCommandError: If the channel is not a ticket.
        """
        async with self._bt.get_connection() as confg:
            # We don't need account for DMs here, due to the guild_only.
            ticket = await confg.fetch_ticket(ctx.channel.id)  # type: ignore
            if ticket is None:
                raise app_commands.AppCommandError(
                    "This channel is not a ticket."
                    " If it is, use /register.")
            if ticket.staff_note_thread is None:
                raise app_commands.AppCommandError(
                    "This ticket has no staff notes.")
            thred = ctx.guild.get_thread(  # type: ignore
                ticket.staff_note_thread)
            if thred is None:
                raise app_commands.AppCommandError(
                    "This ticket's staff notes thread is missing."
                    " Was it deleted?")
            await thred.add_user(ctx.user)
            await ctx.response.send_message("Joined staff notes thread.",
                                            ephemeral=True)

        raise app_commands.AppCommandError("Invalid command execution space.")

    @app_commands.command(name="anonymize",
                          description="Toggle anonymous staff responses.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    async def anonymize(self, ctx: discord.Interaction):
        """Toggle anonymous staff responses.

        This command is used to toggle anonymous staff responses.
        It was requested by a user, so I added it.

        Args:
            ctx: The interaction context.

        Raises:
            AppCommandError: If the command is not executed in a ticket.
        """
        async with self._bt.get_connection() as confg:
            # Checked by discord in decorator
            ticket = await confg.fetch_ticket(ctx.channel.id)  # type: ignore
            if ticket is None:
                raise app_commands.AppCommandError(
                    "This channel is not a ticket.")
            ticket.anonymous = not ticket.anonymous
            await confg.commit()
        await ctx.response.send_message(
            f"Anonymous staff responses are now {ticket.anonymous}.",
            ephemeral=True)

    @app_commands.command(
        name="register",
        description="Register an existing channel as a ticket.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    async def register(self,
                       ctx: discord.Interaction,
                       thread: discord.Thread | None = None):
        """A migration command to register an existing channel as a ticket.

        We have this command to allow users to migrate from the old version,
        or add channels that the bot has missed while it was offline.

        Args:
            ctx: The interaction context.
            thread: The staff notes thread for the ticket.

        Raises:
            AppCommandError: If the channel is already a ticket.
                Or the execution space is not a text channel.
        """
        if isinstance(ctx.channel, discord.TextChannel):
            channel = ctx.channel
            async with self._bt.get_connection() as confg:
                guild = await confg.get_guild(
                    ctx.guild.id)  # type: ignore # checked in decorator
                if thread is None:
                    thread = await channel.create_thread(
                        name="Staff Notes",
                        reason=f"Staff notes for Ticket {channel.name}",
                        auto_archive_duration=10080,
                    )
                    await thread.send(
                        string.Template(guild.open_message).safe_substitute(
                            channel=channel.mention))
                new, ticket = await confg.get_ticket(
                    ctx.channel.id,
                    ctx.guild.id,  # type: ignore
                    thread.id)
                # Unused, we just want to check if it's new and commit it.
                del ticket  # skipcq: PTC-W0043
                if not new:
                    raise app_commands.AppCommandError(
                        "This channel is already a ticket.")
                await confg.commit()
            await ctx.response.send_message("Registered channel as a ticket.",
                                            ephemeral=True)
        raise app_commands.AppCommandError("Invalid command execution space.")


async def setup(bot_instance: bot.TicketsPlus):
    """Sets up up the free commands.

    Called by the bot when the cog is loaded.
    It adds the cog to the bot.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(FreeCommands(bot_instance))
