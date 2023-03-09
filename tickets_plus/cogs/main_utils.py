"""The main cog. Contains 'mainstream' utilities."""
import asyncio
import logging
import re
from string import Template

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.orm import selectinload

from tickets_plus import TicketsPlus
from tickets_plus.database.models import Guild
from tickets_plus.database.statvars import VERSION, Config
from tickets_plus.ext.checks import is_staff_check

CONFG = Config("offline")


class Utility(commands.Cog, name="Main Utilities"):
    """Main bot utilities"""

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
                    guild_bt = self._bt.get_guild(gld.id)
                    if entry.target == channel and await confg.get_ticket_user(
                        entry.user.id, entry.guild.id, True
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
                            observer_ids = guild.get_id_list(
                                "observers_roles", "role_id"
                            )
                            inv = await nts_thrd.send(
                                " ".join([f"<@&{role_id}>" for role_id in observer_ids])
                            )
                            await inv.delete()
                        if guild.strip_buttons:
                            await asyncio.sleep(1)
                            async for msg in channel.history(
                                oldest_first=True, limit=2
                            ):
                                if await confg.get_ticket_user(
                                    msg.author.id, msg.guild.id, True # type: ignore
                                ):
                                    await channel.send(embeds=msg.embeds)
                                    await msg.delete()
                        if guild.community_roles:
                            comm_roles = guild.get_id_list("community_roles", "role_id")
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
                                    rle: discord.Role = guild_bt.get_role(role)  # type: ignore
                                    await channel.set_permissions(
                                        rle, overwrite=overwrite
                                    )
                                except (TypeError, discord.NotFound):
                                    pass
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
            if isinstance(ctx.channel, discord.Thread):
                if isinstance(ctx.channel.parent, discord.TextChannel):
                    await ctx.response.send_message(
                        "Responding to ticket with message:\n" + message
                    )
                    await ctx.channel.parent.send(
                        f"**{guild.staff_team_name}:** " + message
                    )
                else:
                    await ctx.response.send_message(
                        "Cannot respond to forum channel.", ephemeral=True
                    )
                return
            if isinstance(ctx.channel, discord.TextChannel):
                await ctx.response.send_message(
                    "Anonymously responding to ticket with message:\n" + message,
                    ephemeral=True,
                )
                await ctx.channel.send(f"**{guild.staff_team_name}:** " + message)
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
            try:
                await ctx.channel.threads[0].add_user(ctx.user)
            except IndexError:
                await ctx.response.send_message(
                    "No staff notes thread found.", ephemeral=True
                )
                return
            await ctx.response.send_message(
                "Joined the staff notes for this ticket.", ephemeral=True
            )
            return
        await ctx.response.send_message(
            "Invalid command execution space.", ephemeral=True
        )


async def setup(bot: TicketsPlus):
    """Setup function for the cog."""
    await bot.add_cog(Utility(bot))
