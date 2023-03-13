"""This is a event handling extension for Tickets+.

This extension handles all events for Tickets+.
This is used to handle events from Discord.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot = bot.TicketsPlus(...)
    await bot.load_extension("tickets_plus.cogs.events")
    ```
"""
# License: EPL 2.0
import asyncio
import datetime
import logging
import re
import string

import discord
from discord.ext import commands
from discord import utils
from sqlalchemy import orm

from tickets_plus import bot
from tickets_plus.database import models


class Events(commands.Cog, name="Events"):
    """All cog for handling events.

    This cog handles all events for Tickets+.
    This is used to handle events from Discord.
    """

    def __init__(self, bot_instance: bot.TicketsPlus) -> None:
        self._bt = bot_instance
        logging.info("Loaded %s", self.__class__.__name__)

    @commands.Cog.listener(name="on_guild_channel_create")
    async def on_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        """Runs when a channel is created.

        Handles the checking and facilitating of ticket creation.
        This is the main event that handles the creation of tickets.

        Args:
            channel: The channel that was created.
              This is a `discord.abc.GuildChannel` object.
        """
        async with self._bt.get_connection() as confg:
            if isinstance(channel, discord.channel.TextChannel):
                gld = channel.guild
                async for entry in gld.audit_logs(
                    limit=3, action=discord.AuditLogAction.channel_create
                ):
                    if not entry.user:
                        continue
                    guild = await confg.get_guild(
                        gld.id,
                        (
                            orm.selectinload(models.Guild.observers_roles),
                            orm.selectinload(models.Guild.community_roles),
                            orm.selectinload(models.Guild.community_pings),
                        ),
                    )
                    if entry.target == channel and await confg.check_ticket_bot(
                        entry.user.id, gld.id
                    ):
                        nts_thrd: discord.Thread = await channel.create_thread(
                            name="Staff Notes",
                            reason=f"Staff notes for Ticket {channel.name}",
                            auto_archive_duration=10080,
                        )
                        await nts_thrd.send(
                            string.Template(guild.open_message).safe_substitute(
                                channel=channel.mention
                            )
                        )
                        await confg.get_ticket(channel.id, gld.id, nts_thrd.id)
                        logging.info(
                            "Created thread %s for %s", nts_thrd.name, channel.name
                        )
                        if guild.observers_roles:
                            observer_ids = await confg.get_all_observers_roles(gld.id)
                            inv = await nts_thrd.send(
                                " ".join(
                                    [f"<@&{role.role_id}>" for role in observer_ids]
                                )
                            )
                            await inv.delete()
                        if guild.community_roles:
                            comm_roles = await confg.get_all_community_roles(gld.id)
                            overwrite = discord.PermissionOverwrite()
                            overwrite.view_channel = True
                            overwrite.add_reactions = True
                            overwrite.send_messages = True
                            overwrite.read_messages = True
                            overwrite.read_message_history = True
                            overwrite.attach_files = True
                            overwrite.embed_links = True
                            overwrite.use_application_commands = True
                            for role in comm_roles:
                                try:
                                    rle = gld.get_role(role.role_id)
                                    if not rle:
                                        continue
                                    await channel.set_permissions(
                                        rle,
                                        overwrite=overwrite,
                                        reason="Community Support",
                                    )
                                except (TypeError, discord.NotFound):
                                    pass
                        if guild.community_pings:
                            comm_pings = await confg.get_all_community_pings(gld.id)
                            inv = await channel.send(
                                " ".join([f"<@&{role.role_id}>" for role in comm_pings])
                            )
                            await asyncio.sleep(0.25)
                            await inv.delete()
                        if guild.strip_buttons:
                            await asyncio.sleep(1)
                            async for msg in channel.history(
                                oldest_first=True, limit=2
                            ):
                                if await confg.check_ticket_bot(msg.author.id, gld.id):
                                    await channel.send(embeds=msg.embeds)
                                    await msg.delete()
                        descr = (
                            f"Ticket {channel.name}\n"
                            + f"Opened at <t:{int(channel.created_at.timestamp())}:f>"
                        )
                        if guild.first_autoclose:
                            descr += f"\nCloses at <t:{int((channel.created_at + datetime.timedelta(minutes=guild.first_autoclose)).timestamp())}:R>"  # skipcq: FLK-E501 # pylint: disable=line-too-long
                            descr += "If no one responds, the ticket will be closed automatically. Thank you for your patience!"  # skipcq: FLK-E501 # pylint: disable=line-too-long
                        await channel.edit(
                            topic=descr, reason="More information for the ticket."
                        )
                        await confg.commit()

    @commands.Cog.listener(name="on_guild_channel_delete")
    async def on_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        """Cleanups for when a ticket is deleted.

        This is the main event that handles the deletion of tickets.
        It is used to delete the ticket from the database.

        Args:
            channel: The channel that was deleted.
              This is a `discord.abc.GuildChannel` object.
        """
        if isinstance(channel, discord.channel.TextChannel):
            async with self._bt.get_connection() as confg:
                ticket = await confg.fetch_ticket(channel.id)
                if ticket:
                    await confg.delete(ticket)
                    logging.info("Deleted ticket %s", channel.name)
                    await confg.commit()

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message) -> None:
        """Handles all message-related features.

        We use this to handle the message discovery feature.
        Adittionally, we use this if a ticket is in anonymous mode.

        Args:
            message: The message that was sent.
              This is a `discord.Message` object.
        """
        async with self._bt.get_connection() as confg:
            if message.author.bot or message.guild is None:
                return
            guild = await confg.get_guild(message.guild.id)
            if guild.msg_discovery:
                alpha = re.search(
                    r"https:\/\/(?:canary\.)?discord\.com\/channels\/(?P<srv>\d{18})\/(?P<cha>\d{18})\/(?P<msg>\d*)",  # skipcq: FLK-E501 # pylint: disable=line-too-long
                    message.content,
                )
                if alpha:
                    try:  # We do not check any types in this block as we are catching the errors.
                        gld = self._bt.get_guild(int(alpha.group("srv")))
                        chan = gld.get_channel_or_thread(int(alpha.group("cha")))  # type: ignore
                        got_msg = await chan.fetch_message(int(alpha.group("msg")))  # type: ignore
                    except (
                        AttributeError,
                        discord.HTTPException,
                    ):
                        logging.warning("Message discovery failed.")
                    else:
                        time = got_msg.created_at.strftime("%d/%m/%Y %H:%M:%S")
                        if not got_msg.content and got_msg.embeds:
                            discovered_result = got_msg.embeds[0]
                            discovered_result.set_footer(
                                text=f"[EMBED CAPTURED] Sent in {chan.name}"  # type: ignore
                                f" at {time}"
                            )
                        else:
                            discovered_result = discord.Embed(
                                description=got_msg.content, color=0x0D0EB4
                            )
                            discovered_result.set_footer(
                                text=f"Sent in {chan.name} at {time}"  # type: ignore
                            )
                        discovered_result.set_author(
                            name=got_msg.author.name,
                            icon_url=got_msg.author.display_avatar.url,
                        )
                        discovered_result.set_image(
                            url=got_msg.attachments[0].url
                            if got_msg.attachments
                            else None
                        )
                        await message.reply(embed=discovered_result)
            ticket = await confg.fetch_ticket(message.channel.id)
            if ticket:
                # Make sure the ticket exists
                if ticket.anonymous:
                    staff = False
                    staff_roles = await confg.get_all_staff_roles(guild.guild_id)
                    for role in staff_roles:
                        parsed_role = message.guild.get_role(role.role_id)
                        if parsed_role in message.author.roles:  # type: ignore
                            # Alredy checked for member
                            staff = True
                            break
                    if not staff:
                        return
                    await message.channel.send(
                        f"**{guild.staff_team_name}:** "
                        + utils.escape_mentions(message.content),
                        embeds=message.embeds,
                    )
                    await message.delete()


async def setup(bot_instance: bot.TicketsPlus) -> None:
    """Setup function for the cog.

    This is called when the cog is loaded.
    It adds the cog to the bot.

    Args:
      bot: The bot that is loading the cog.
        This is a TicketsPlus object."""
    await bot_instance.add_cog(Events(bot_instance))
