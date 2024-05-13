"""Staff-only commands cog for Tickets+.

Seperated from the main cog to keep things clean.
Keeps the staff-only commands in clear view.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlusBot(...)
    await bot_instance.load_extension("tickets_plus.cogs.staff")
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contributor, GPL-3.0-or-later.

import datetime
import logging
import string

import discord
from discord import app_commands, utils
from discord.ext import commands

from tickets_plus import bot
from tickets_plus.ext import checks, exceptions


class StaffCmmd(commands.Cog, name="StaffCommands"):
    """Staff-only commands for Tickets+.

    This cog contains all staff-only commands. These commands are
    only available to users with the staff role, and are used to
    manage the bot and the tickets.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot) -> None:
        """Initialises the cog instance.

        We store some attributes here for later use.

        Args:
            bot_instance: The bot instance.
        """
        self._bt = bot_instance
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="respond", description="Respond to a ticket as the bot.")
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
            guild = await confg.get_guild(ctx.guild_id)  # type: ignore # checked in decorator
            if not ctx.user.resolved_permissions.mention_everyone:
                message = utils.escape_mentions(message)
            if isinstance(ctx.channel, discord.Thread):
                ticket = await confg.fetch_ticket(ctx.channel.parent.id)
                if ticket is None:
                    raise exceptions.InvalidLocation("The parent channel is not a ticket.")
                if ticket.staff_note_thread != ctx.channel.id:
                    raise exceptions.InvalidLocation("This channel is not the designated staff"
                                                     " notes thread.")
                await ctx.followup.send(f"Responding to ticket with message:\n{message}")
                await ctx.channel.parent.send(  # type: ignore
                    f"**{guild.staff_team_name}:** {message}")

            elif isinstance(ctx.channel, discord.TextChannel):
                ticket = await confg.fetch_ticket(ctx.channel.id)
                if ticket is None:
                    raise exceptions.InvalidLocation("This channel is not a ticket."
                                                     " If it is, use /register.")
                await ctx.followup.send(
                    f"Responding to ticket with message:\n{message}",
                    ephemeral=True,
                )
                await ctx.channel.send(f"**{guild.staff_team_name}:** {message}")

            await confg.close()

    @app_commands.command(name="join", description="Join a ticket's staff notes.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    async def join(self, ctx: discord.Interaction) -> None:
        """Adds the user to the ticket's staff note thread.

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
            # We don't need an account for DMs here, due to the guild_only.
            ticket = await confg.fetch_ticket(ctx.channel.id)  # type: ignore
            if ticket is None:
                raise exceptions.InvalidLocation("This channel is not a ticket."
                                                 " If it is, use /register.")
            if ticket.staff_note_thread is None:
                raise exceptions.InvalidLocation("This ticket has no staff notes.")
            thred = ctx.guild.get_thread(  # type: ignore
                ticket.staff_note_thread)
            if thred is None:
                raise exceptions.ReferenceNotFound("This ticket's staff notes thread is missing."
                                                   " Was it deleted?")
            emd = discord.Embed(title="Success!",
                                description="You have joined the staff notes thread.",
                                color=discord.Color.green())
            await thred.add_user(ctx.user)
            await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="anonymize", description="Toggle anonymous staff responses.")
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
                raise exceptions.InvalidLocation("This channel is not a ticket.")
            ticket.anonymous = not ticket.anonymous
            status = ticket.anonymous
            await confg.commit()
        emd = discord.Embed(title="Success!",
                            description=f"Anonymous staff responses are now {status}.",
                            color=discord.Color.green() if status else discord.Color.red())
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="register", description="Register an existing channel as a ticket.")
    @app_commands.describe(thread="The staff notes thread for the ticket.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    async def register(self, ctx: discord.Interaction, thread: discord.Thread | None = None) -> None:
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
                guild = await confg.get_guild(ctx.guild_id)  # type: ignore # checked in decorator
                if thread is None and guild.legacy_threads:
                    thread = await channel.create_thread(
                        name="Staff Notes",
                        reason=f"Staff notes for Ticket {channel.name}",
                        auto_archive_duration=10080,
                    )
                    await thread.send(string.Template(guild.open_message).safe_substitute(channel=channel.mention))
                new, ticket = await confg.get_ticket(
                    ctx.channel.id,
                    ctx.guild_id,  # type: ignore
                    thread.id)
                # Unused, we just want to check if it's new and commit it.
                del ticket
                if not new:
                    raise exceptions.InvalidLocation("This channel is already a ticket.")
                await confg.commit()
            emd = discord.Embed(title="Success!",
                                description="Registered channel as a ticket.",
                                color=discord.Color.green())
            await ctx.followup.send(embed=emd, ephemeral=True)
            return
        raise exceptions.InvalidLocation("Invalid command execution space.")

    @app_commands.command(name="usrstatus", description="Set a new user status.")
    @app_commands.guild_only()
    @checks.is_staff_check()
    @app_commands.describe(
        target="The user to set the status for.",
        status="The new status.",
        days="The new status time days.",
        hours="The new status time hours.",
        minutes="The new status time minutes.",
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="None", value=0),
        app_commands.Choice(name="Support Blocked", value=1),
        app_commands.Choice(name="Community Support Blocked", value=2),
    ])
    async def usrstatus(self,
                        interaction: discord.Interaction,
                        target: discord.Member,
                        status: app_commands.Choice[int],
                        days: int = 0,
                        hours: int = 0,
                        minutes: int = 0) -> None:
        """Set a new user status.

        This command is used to set a new user status.
        It's used to block users from opening tickets or from getting support.

        Args:
            interaction: Discord interaction.
            target: The user to set the status for.
            status: The new status.
            days: The new status time days.
            hours: The new status time hours.
            minutes: The new status time minutes.
        """
        await interaction.response.defer(ephemeral=True)
        async with self._bt.get_connection() as confg:
            member = await confg.get_member(
                target.id,
                interaction.guild_id  # type: ignore
            )
            member.status = status.value
            if status.value == 0:
                member.status_till = None
                await confg.commit()
                emd = discord.Embed(title="Success!",
                                    description=f"Removed status from {target.mention}.",
                                    color=discord.Color.green())
                emd2 = discord.Embed(title="Status Removed",
                                     description=(f"Your status in {target.guild.name} has been removed"
                                                  f" by {interaction.user.display_name}."),
                                     color=discord.Color.green())
            else:
                if days + hours + minutes == 0:
                    penalty_time = "Indefinitely"
                    member.status_till = None
                else:
                    penalty_time = datetime.timedelta(days=days, hours=hours, minutes=minutes)
                    member.status_till = utils.utcnow() + penalty_time
                if status.value == 1:
                    if member.guild.support_block is None:
                        raise exceptions.InvalidParameters("The support block role has not been set.\n"
                                                           "This may be intentional.\n"
                                                           "If not please set it up using the /settings.")
                    await target.add_roles(discord.Object(member.guild.support_block))
                    emd = discord.Embed(title="Success!",
                                        description=(f"Blocked {target.mention} from opening tickets"
                                                     f" for {str(penalty_time)}."),
                                        color=discord.Color.red())
                    emd2 = discord.Embed(title="Support Blocked",
                                         description=("You have been blocked from opening tickets from"
                                                      f" {target.guild.name} for {str(penalty_time)}."),
                                         color=discord.Color.red())
                else:
                    if member.guild.helping_block is None:
                        raise exceptions.InvalidParameters("The helping block role has not been set.\n"
                                                           "This may be intentional.\n"
                                                           "If not please set it up using the /settings.")
                    await target.add_roles(discord.Object(member.guild.helping_block))
                    emd = discord.Embed(title="Success!",
                                        description=(f"Blocked {target.mention} "
                                                     f"from providing support for {str(penalty_time)}."),
                                        color=discord.Color.red())
                    emd2 = discord.Embed(title="Community Support Blocked",
                                         description=("You have been blocked from providing "
                                                      f"support from {target.guild.name}"
                                                      f" for {str(penalty_time)}."),
                                         color=discord.Color.red())
                    if member.guild.strip_roles:
                        roles = await confg.get_all_community_roles(interaction.guild_id)  # type: ignore
                        unpck = [discord.Object(rle.role_id) for rle in roles]
                        await target.remove_roles(*unpck, reason="Community Support Blocked")
            await confg.commit()
        await interaction.followup.send(embed=emd, ephemeral=True)
        try:
            await target.send(embed=emd2)
        except discord.Forbidden:
            logging.debug("Failed to send status message to user.")


async def setup(bot_instance: bot.TicketsPlusBot) -> None:
    """Setup function for the StaffCmmd cog.

    Adds the StaffCmmd cog to the bot.
    Automatically called by the bot.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(StaffCmmd(bot_instance))
