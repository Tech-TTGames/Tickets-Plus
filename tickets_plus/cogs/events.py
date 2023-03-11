"""Events cog for Tickets+."""
import asyncio
import logging
import re
from string import Template

import discord
from discord.ext import commands
from sqlalchemy.orm import selectinload

from tickets_plus.bot import TicketsPlus
from tickets_plus.database.models import Guild


class Events(commands.Cog, name="Events"):
    """All events for Tickets+."""

    def __init__(self, bot: TicketsPlus):
        self._bt = bot
        logging.info("Loaded %s", self.__class__.__name__)

    @commands.Cog.listener(name="on_guild_channel_create")
    async def on_channel_create(self, channel):
        """
        EXTENSION 1 + 3: Staff notes for Tickets! and button stripping.
        Minor Extension 2: Safe Community Support

        This event works based on the ticket_users configuration.

        Please ensure you add your Ticket bot ID or approved
        Ticket invoking user IDs to the config file or via commands.
        """
        async with self._bt.get_connection() as confg:
            if isinstance(channel, discord.channel.TextChannel):
                gld = channel.guild
                async for entry in gld.audit_logs(
                    limit=3, action=discord.AuditLogAction.channel_create
                ):
                    if entry.user is None:
                        continue
                    guild = await confg.get_guild(
                        gld.id, (selectinload(Guild.observers_roles),)
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
                            Template(guild.open_message).safe_substitute(
                                channel=channel.mention
                            )
                        )
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
                                    if rle is None:
                                        continue
                                    await channel.set_permissions(
                                        rle, overwrite=overwrite
                                    )
                                except (TypeError, discord.NotFound):
                                    pass
                        if guild.strip_buttons:
                            await asyncio.sleep(1)
                            async for msg in channel.history(
                                oldest_first=True, limit=2
                            ):
                                if await confg.check_ticket_bot(msg.author.id, gld.id):
                                    await channel.send(embeds=msg.embeds)
                                    await msg.delete()
            await confg.close()

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message) -> None:
        """
        Minor Extension: Message Discovery
        Displays the message linked to as an embed.
        """
        async with self._bt.get_connection() as confg:
            if message.author.bot or message.guild is None:
                return
            guild = await confg.get_guild(message.guild.id)
            if guild.msg_discovery:
                alpha = re.search(
                    r"https:\/\/(?:canary\.)?discord\.com\/channels\/(?P<srv>\d{18})\/(?P<cha>\d{18})\/(?P<msg>\d*)",  # skipcq: FLK-E501 # pylint: disable=line-too-long
                    message.content,
                )  # pylint: disable=line-too-long
                if alpha:
                    try:
                        chan = self._bt.get_guild(int(alpha.group("srv"))).get_channel_or_thread(int(alpha.group("cha")))  # type: ignore pylint: disable=line-too-long
                        got_msg = await chan.fetch_message(int(alpha.groupdict()["msg"]))  # type: ignore # pylint: disable=line-too-long
                    except:  # pylint: disable=bare-except
                        return
                    data = discord.Embed(description=got_msg.content, color=0x0D0EB4)
                    data.set_author(name=got_msg.author.name, icon_url=got_msg.author.avatar.url)  # type: ignore # pylint: disable=line-too-long
                    data.set_footer(text=f"Sent in {got_msg.channel.name} at {got_msg.created_at}")  # type: ignore # pylint: disable=line-too-long
                    data.set_image(
                        url=got_msg.attachments[0].url if got_msg.attachments else None
                    )
                    await message.reply(embed=data)
            await confg.close()


async def setup(bot: TicketsPlus):
    """Setup function for the cog."""
    await bot.add_cog(Events(bot))
