'''
The main cog. Contains 'mainstream' utilities.
'''
import logging

import discord
from discord import app_commands
from discord.ext import commands

from variables import VERSION, Config


class Utility(commands.Cog, name="Main Bot Utilites"):
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
