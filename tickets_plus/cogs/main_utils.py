"""Miscellaneous commands that don't fit anywhere else.

They are various commands that don't fit into any other category.
They are in free discord commands not assigned to groups.
If the comamnd set warrants it, we may move it to a group.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlusBot(...)
    await bot_instance.load_extension("tickets_plus.cogs.main_utils")
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import logging
import string

import discord
from discord import app_commands, utils
from discord.ext import commands

from tickets_plus import bot
from tickets_plus.database import statvars
from tickets_plus.ext import checks, exceptions


class FreeCommands(commands.Cog, name="General Random Commands"):
    """General commands that don't fit anywhere else.

    We assign various commands that don't fit anywhere else to this cog.
    They are in free discord commands not assigned to groups.
    If a context is big enough, we may move it to a group.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot):
        """Initialise the FreeCommands cog.

        We initialise some attributes here for later use.

        Args:
            bot_instance: The bot instance that loaded this cog.
        """
        self._bt = bot_instance
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(
        name="ping",
        description="The classic ping command. Checks the bot's latency.")
    async def ping(self, ctx: discord.Interaction) -> None:
        """The classic ping command. Checks the bot's latency.

        This command is used to check the bot's latency.
        It responds with the bot's latency in milliseconds.

        Args:
            ctx: The interaction context.
        """
        embd = discord.Embed(title="Pong!",
                             description=f"The bot is online.\nPing: "
                             f"{str(round(self._bt.latency * 1000))}ms",
                             color=discord.Color.green())
        await ctx.response.send_message(embed=embd)

    @app_commands.command(name="version", description="Get the bot's version.")
    async def version(self, ctx: discord.Interaction) -> None:
        """This command is used to check the bot's version.

        Responds with the bot's version and a link to the source code.

        Args:
            ctx: The interaction context.
        """
        emd = discord.Embed(
            title="Tickets+",
            description=f"Bot version: {statvars.VERSION}\n"
            "This bot is open source and experimental!",
            color=discord.Color.from_str("0x00FFFF"),
        ).add_field(
            name="Source Code:",
            value=(
                "[Available on GitHub](https://github.com/Tech-TTGames/Tickets-Plus)"  # pylint: disable=line-too-long # skipcq: PYL-W0511, FLK-W505
                "\nThis is the place to report bugs and suggest features."),
        )
        # .add_field(name="Get Support:",
        #            value="[Join the support server](<NO SUPPORT SERVER YET>)")
        await ctx.response.send_message(embed=emd)

    @app_commands.command(name="invite",
                          description="Invite the bot to a server.")
    async def invite(self, ctx: discord.Interaction) -> None:
        """Invite the bot to a server.

        This command is used to invite the bot to a server.
        It responds with a link to invite the bot to a server.

        Args:
            ctx: The interaction context.
        """
        app = await ctx.client.application_info()
        admn_perms = discord.Permissions(8)
        safe_perms = discord.Permissions(535059492048)
        if app.bot_public:
            emd = discord.Embed(
                title="Tickets+",
                description="Invite the bot to your server with this links:\n",
                color=discord.Color.from_str("0x00FFFF"))
            emd.add_field(
                name="Admin Permissions:",
                value=(
                    f"[Click Here!]({utils.oauth_url(app.id,permissions=admn_perms)})"  # pylint: disable=line-too-long # skipcq: PYL-W0511, FLK-W505
                ),
            )
            emd.add_field(
                name="Safe Permissions:",
                value=(
                    f"[Click Here!]({utils.oauth_url(app.id,permissions=safe_perms)})"  # pylint: disable=line-too-long # skipcq: PYL-W0511, FLK-W505
                ),
            )
        else:
            flg = False
            if app.team:
                # Split to avoid errors ie AttributeError
                if ctx.user in app.team.members:
                    flg = True
            if ctx.user == app.owner:
                flg = True
            if flg:
                emd = discord.Embed(
                    title="Tickets+",
                    description="Welcome back authorised user!\n"
                    "Invite the bot to your server with this link:\n",
                    color=discord.Color.from_str("0x00FFFF"))
                emd.add_field(
                    name="Invite Link:",
                    value=(
                        f"[Click Here!]({utils.oauth_url(app.id,permissions=admn_perms)})"  # pylint: disable=line-too-long # skipcq: PYL-W0511, FLK-W505
                    ),
                )
            else:
                emd = discord.Embed(
                    title="Tickets+",
                    description="Sorry! This instance of the bot is not public."
                    " You can't invite it to your server.",
                    color=discord.Color.red())
        await ctx.response.send_message(embed=emd)

    @app_commands.command(name="respond",
                          description="Respond to a ticket as the bot.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    @app_commands.describe(message="The message to send to the ticket.")
    async def respond(self, ctx: discord.Interaction, message: str) -> None:
        """Respond to a ticket as the bot.

        This command is used to respond to a ticket as the bot.
        It can be used in a ticket channel or a staff notes thread.
        It then sends the message to the ticket as the bot.

        Args:
            ctx: The interaction context.
            message: The message to send to the ticket.

        Raises:
            `tickets_plus.ext.exceptions.InvalidLocation`: Wrong location.
                Raised if the command is used in a channel that is not a ticket
                or a staff notes thread.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as confg:
            guild = await confg.get_guild(
                ctx.guild.id)  # type: ignore # checked in decorator
            sanitized_message = utils.escape_mentions(message)
            if isinstance(ctx.channel, discord.Thread):
                ticket = await confg.fetch_ticket(
                    ctx.channel.parent.id  # type: ignore
                )
                if ticket is None:
                    raise exceptions.InvalidLocation(
                        "The parent channel is not a ticket.")
                if ticket.staff_note_thread != ctx.channel.id:
                    raise exceptions.InvalidLocation(
                        "This channel is not the designated staff"
                        " notes thread.")
                await ctx.followup.send(
                    f"Responding to ticket with message:\n{sanitized_message}")
                await ctx.channel.parent.send(  # type: ignore
                    f"**{guild.staff_team_name}:** {sanitized_message}")

            elif isinstance(ctx.channel, discord.TextChannel):
                ticket = await confg.fetch_ticket(ctx.channel.id)
                if ticket is None:
                    raise exceptions.InvalidLocation(
                        "This channel is not a ticket."
                        " If it is, use /register.")
                await ctx.followup.send(
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
    async def join(self, ctx: discord.Interaction) -> None:
        """Adds the user to the ticket's staff notes thread.

        This command is used to add the user to the ticket's staff notes thread.
        It's used to allow staff to join notes without the need for the
        user to have the Manage Threads permission.

        Args:
            ctx: The interaction context.

        Raises:
            `tickets_plus.ext.exceptions.InvalidLocation`: Wrong location.
                Raised if the command is used in a channel that is not a ticket
                or there is no staff notes thread.
            `tickets_plus.ext.exceptions.ReferenceNotFound`: Thread missing.
                Raised if the staff notes thread is missing.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as confg:
            # We don't need account for DMs here, due to the guild_only.
            ticket = await confg.fetch_ticket(ctx.channel.id)  # type: ignore
            if ticket is None:
                raise exceptions.InvalidLocation("This channel is not a ticket."
                                                 " If it is, use /register.")
            if ticket.staff_note_thread is None:
                raise exceptions.InvalidLocation(
                    "This ticket has no staff notes.")
            thred = ctx.guild.get_thread(  # type: ignore
                ticket.staff_note_thread)
            if thred is None:
                raise exceptions.ReferenceNotFound(
                    "This ticket's staff notes thread is missing."
                    " Was it deleted?")
            emd = discord.Embed(
                title="Success!",
                description="You have joined the staff notes thread.",
                color=discord.Color.green())
            await thred.add_user(ctx.user)
            await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="anonymize",
                          description="Toggle anonymous staff responses.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    async def anonymize(self, ctx: discord.Interaction) -> None:
        """Toggle anonymous staff responses.

        This command is used to toggle anonymous staff responses.
        The implementation itself is in events.py.

        Args:
            ctx: The interaction context.

        Raises:
            `tickets_plus.ext.exceptions.InvalidLocation`: Wrong location.
                Raised if the command is used in a channel that is not a ticket.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as confg:
            # Checked by discord in decorator
            ticket = await confg.fetch_ticket(ctx.channel.id)  # type: ignore
            if ticket is None:
                raise exceptions.InvalidLocation(
                    "This channel is not a ticket.")
            ticket.anonymous = not ticket.anonymous
            status = ticket.anonymous
            await confg.commit()
        emd = discord.Embed(
            title="Success!",
            description=f"Anonymous staff responses are now {status}.",
            color=discord.Color.green() if status else discord.Color.red())
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(
        name="register",
        description="Register an existing channel as a ticket.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    async def register(self,
                       ctx: discord.Interaction,
                       thread: discord.Thread | None = None) -> None:
        """A migration command to register an existing channel as a ticket.

        We have this command to allow users to migrate from the old version,
        or add channels that the bot has missed while it was offline.
        It basically just tells the bot to start tracking the channel.

        Args:
            ctx: The interaction context.
            thread: The staff notes thread for the ticket.

        Raises:
            `tickets_plus.ext.exceptions.InvalidLocation`: Wrong location.
                If the channel is already a ticket.
                Or the execution space is not a text channel.
        """
        await ctx.response.defer(ephemeral=True)
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
                    raise exceptions.InvalidLocation(
                        "This channel is already a ticket.")
                await confg.commit()
            emd = discord.Embed(title="Success!",
                                description="Registered channel as a ticket.",
                                color=discord.Color.green())
            await ctx.followup.send(embed=emd, ephemeral=True)
            return
        raise exceptions.InvalidLocation("Invalid command execution space.")


async def setup(bot_instance: bot.TicketsPlusBot) -> None:
    """Sets up up the free commands.

    Called by the bot when the cog is loaded.
    It adds the cog to the bot.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(FreeCommands(bot_instance))
