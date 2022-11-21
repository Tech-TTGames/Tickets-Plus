'''
The main cog. Contains 'mainstream' utilities.
'''
import logging
import re

import discord
from discord import app_commands
from discord.ext import commands

from variables import VERSION, Config

CONFG = Config('offline')

class Utility(commands.Cog, name="Main Utilities"):
    '''Main bot utilities'''
    def __init__(self, bot: commands.Bot, config: Config):
        self._config = config
        self._bt = bot
        logging.info("Loaded %s", self.__class__.__name__)

    @commands.Cog.listener(name="on_guild_channel_create")
    async def on_channel_create(self, channel):
        '''EXTENSION 1: Staff notes for tickets!'''
        if isinstance(channel, discord.channel.TextChannel):
            gld = channel.guild
            cnfg = self._config
            async for entry in gld.audit_logs(limit=3,
                                             action=discord.AuditLogAction.channel_create):
                if entry.user is None:
                    continue
                if entry.target == channel and entry.user.id in cnfg.ticket_users:
                    nts_thrd: discord.Thread = await channel.create_thread(name="Staff Notes",
                     reason=f"Staff notes for Ticket {channel.name}",auto_archive_duration=10080)
                    await nts_thrd.send(cnfg.open_msg.safe_substitute(channel=channel.mention))
                    logging.info("Created thread %s for %s", nts_thrd.name, channel.name)
                    if self._config.staff_ping:
                        inv = await nts_thrd.send(" ".join([role.mention for role in cnfg.staff]))
                        await inv.delete()

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message) -> None:
        '''Minor Extension: Message Discovery
        Displays the message linked to as an embed.'''
        if message.author.bot:
            return
        if self._bt.intents.message_content:
            alpha = re.search(r"https:\/\/(?:canary\.)?discord\.com\/channels\/(?P<srv>\d{18})\/(?P<cha>\d{18})\/(?P<msg>\d*)",message.content) # pylint: disable=line-too-long
            if alpha:
                try:
                    chan = self._bt.get_guild(int(alpha.group('srv'))).get_channel_or_thread(int(alpha.group('cha'))) #type: ignore pylint: disable=line-too-long
                    got_msg = await chan.fetch_message(int(alpha.groupdict()["msg"])) # type: ignore # pylint: disable=line-too-long
                except: # pylint: disable=bare-except
                    return
                data = discord.Embed(description=got_msg.content, color=0x0d0eb4)
                data.set_author(name=got_msg.author.name, icon_url=got_msg.author.avatar.url) # type: ignore # pylint: disable=line-too-long
                data.set_footer(text=f"Sent in {got_msg.channel.name} at {got_msg.created_at}")
                data.set_image(url=got_msg.attachments[0].url if got_msg.attachments else None)
                await message.reply(embed=data)

    @app_commands.command(name="ping",
                         description="The classic ping command. Checks the bot's latency.")
    async def ping(self, ctx):
        """This command is used to check if the bot is online."""
        await ctx.response.send_message("Pong! The bot is online.\nPing: " + \
                str(round(self._bt.latency * 1000)) + "ms")
        await self._bt.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
              name="with tickets!"))

    @app_commands.command(name="version", description="Get the bot's version.")
    async def version(self, ctx: discord.Interaction):
        """This command is used to check the bot's version."""
        await ctx.response.send_message("Bot 'Tickets Plus' version: " + \
                  VERSION + " by Tech. TTGames#8616\n" + \
                  "This bot is open source and experimental!" + \
                  "Check it out and report issues at https://github.com/Tech-TTGames/Tickets-Plus")

    @app_commands.command(name="respond", description="Respond to a ticket as the bot.")
    @commands.has_any_role(*CONFG.staff_ids)
    async def respond(self, ctx: discord.Interaction, message: str):
        """EXTENSION 2: Anonymised staff responses.
        This command is used to respond to a ticket as the bot."""
        if isinstance(ctx.channel, discord.Thread):
            if isinstance(ctx.channel.parent, discord.TextChannel):
                await ctx.response.send_message("Responding to ticket with message:\n" + message)
                await ctx.channel.parent.send(f"**{self._config.staff_team}:** " + message)
            else:
                await ctx.response.send_message("Cannot respond to forum channel.", ephemeral=True)
            return
        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.response.send_message("Anonymously responding to ticket with message:\n"
                  + message, ephemeral=True)
            await ctx.channel.send(f"**{self._config.staff_team}:** " + message)

async def setup(bot: commands.Bot):
    '''Setup function for the cog.'''
    global CONFG # pylint: disable=global-statement
    CONFG = Config(bot)
    await bot.add_cog(Utility(bot, Config(bot)))
