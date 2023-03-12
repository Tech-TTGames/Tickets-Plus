"""Random commands that don't fit anywhere else."""
import logging
from string import Template
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import escape_mentions

from tickets_plus.bot import TicketsPlus
from tickets_plus.database.statvars import VERSION
from tickets_plus.ext.checks import is_staff_check


class FreeCommands(commands.Cog, name="General Random Commands"):
    """General commands that don't fit anywhere else"""

    def __init__(self, bot: TicketsPlus):
        self._bt = bot
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(
        name="ping", description="The classic ping command. Checks the bot's latency."
    )
    async def ping(self, ctx: discord.Interaction):
        """This command is used to check if the bot is online."""
        await ctx.response.send_message(
            "Pong! The bot is online.\nPing: "
            + str(round(self._bt.latency * 1000))
            + "ms"
        )

    @app_commands.command(name="version", description="Get the bot's version.")
    async def version(self, ctx: discord.Interaction):
        """This command is used to check the bot's version."""
        await ctx.response.send_message(
            "Bot 'Tickets Plus' version: "
            + VERSION
            + " by Tech. TTGames#8616\n"
            + "This bot is open source and experimental!\n"
            + "Check it out and report issues at https://github.com/Tech-TTGames/Tickets-Plus"
        )

    @app_commands.command(name="respond", description="Respond to a ticket as the bot.")
    @app_commands.guild_only()
    @is_staff_check()
    @app_commands.describe(message="The message to send to the ticket.")
    async def respond(self, ctx: discord.Interaction, message: str):
        """
        EXTENSION 2: Anonymised staff responses.
        This command is used to respond to a ticket as the bot.
        """
        async with self._bt.get_connection() as confg:
            guild = await confg.get_guild(ctx.guild.id)  # type: ignore # checked in decorator
            sanitized_message = escape_mentions(message)
            if isinstance(ctx.channel, discord.Thread):
                ticket = await confg.fetch_ticket(ctx.channel.parent.id)  # type: ignore
                if ticket is None:
                    await ctx.response.send_message(
                        "This channel is not a ticket.", ephemeral=True
                    )
                    raise app_commands.AppCommandError("This channel is not a ticket.")
                if ticket.staff_note_thread != ctx.channel.id:
                    await ctx.response.send_message(
                        "This channel is not a staff notes thread.", ephemeral=True
                    )
                    raise app_commands.AppCommandError(
                        "This channel is not a staff notes thread."
                    )
                await ctx.response.send_message(
                    "Responding to ticket with message:\n" + sanitized_message
                )
                await ctx.channel.parent.send(  # type: ignore
                    f"**{guild.staff_team_name}:** {sanitized_message}"
                )

            elif isinstance(ctx.channel, discord.TextChannel):
                ticket = await confg.fetch_ticket(ctx.channel.id)
                if ticket is None:
                    await ctx.response.send_message(
                        "This channel is not a ticket.", ephemeral=True
                    )
                    raise app_commands.AppCommandError("This channel is not a ticket.")
                await ctx.response.send_message(
                    "Responding to ticket with message:\n" + sanitized_message,
                    ephemeral=True,
                )
                await ctx.channel.send(
                    f"**{guild.staff_team_name}:** {sanitized_message}"
                )

            await confg.close()

    @app_commands.command(name="join", description="Join a ticket's staff notes.")
    @app_commands.guild_only()
    @is_staff_check()
    async def join(self, ctx: discord.Interaction):
        """
        EXTENSION 3: Staff notes.
        This command is used to join a ticket's staff notes.
        """
        if isinstance(ctx.channel, discord.TextChannel):
            async with self._bt.get_connection() as confg:
                ticket = await confg.fetch_ticket(ctx.channel.id)
                if ticket is None:
                    await ctx.response.send_message(
                        "This channel is not a ticket.", ephemeral=True
                    )
                    raise app_commands.AppCommandError("This channel is not a ticket.")
                if ticket.staff_note_thread is None:
                    await ctx.response.send_message(
                        "This ticket has no staff notes.", ephemeral=True
                    )
                    raise app_commands.AppCommandError(
                        "This ticket has no staff notes."
                    )
                thred = ctx.guild.get_thread(ticket.staff_note_thread)  # type: ignore
                if thred is None:
                    await ctx.response.send_message(
                        "This ticket's staff notes thread is missing.", ephemeral=True
                    )
                    raise app_commands.AppCommandError(
                        "This ticket's staff notes thread is missing."
                    )
                await thred.add_user(ctx.user)
                await ctx.response.send_message(
                    "Joined staff notes thread.", ephemeral=True
                )

        await ctx.response.send_message(
            "Invalid command execution space.", ephemeral=True
        )
        raise app_commands.AppCommandError("Invalid command execution space.")

    @app_commands.command(
        name="anonymize", description="Toggle anonymous staff responses."
    )
    @app_commands.guild_only()
    @is_staff_check()
    async def anonymize(self, ctx: discord.Interaction):
        """As requested by a user, this command is used to toggle anonymous staff responses."""
        if isinstance(ctx.channel, discord.TextChannel):
            async with self._bt.get_connection() as confg:
                ticket = await confg.fetch_ticket(ctx.channel.id)
                if ticket is None:
                    await ctx.response.send_message(
                        "This channel is not a ticket.", ephemeral=True
                    )
                    raise app_commands.AppCommandError("This channel is not a ticket.")
                ticket.anonymous = not ticket.anonymous
                await confg.commit()
                await confg.close()
            await ctx.response.send_message(
                f"Anonymous staff responses are now {ticket.anonymous}.", ephemeral=True
            )

    @app_commands.command(
        name="register", description="Register an existing channel as a ticket."
    )
    @app_commands.guild_only()
    @is_staff_check()
    async def register(
        self, ctx: discord.Interaction, thread: Optional[discord.Thread]
    ):
        """A migration command to register an existing channel as a ticket."""
        if isinstance(ctx.channel, discord.TextChannel):
            channel = ctx.channel
            async with self._bt.get_connection() as confg:
                guild = await confg.get_guild(ctx.guild.id)  # type: ignore # checked in decorator
                if thread is None:
                    thread = await channel.create_thread(
                        name="Staff Notes",
                        reason=f"Staff notes for Ticket {channel.name}",
                        auto_archive_duration=10080,
                    )
                    await thread.send(
                        Template(guild.open_message).safe_substitute(
                            channel=channel.mention
                        )
                    )
                ticket = await confg.get_ticket(
                    ctx.channel.id, ctx.guild.id, thread.id  # type: ignore
                )
                if ticket is not None:
                    await ctx.response.send_message(
                        "This channel is already a ticket.", ephemeral=True
                    )
                    raise app_commands.AppCommandError(
                        "This channel is already a ticket."
                    )
                await confg.commit()
                await confg.close()
            await ctx.response.send_message(
                "Registered channel as a ticket.", ephemeral=True
            )


async def setup(bot: TicketsPlus):
    """Setup function for the cog."""
    await bot.add_cog(FreeCommands(bot))
