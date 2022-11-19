'''
The main cog. Contains 'mainstream' utilities.
'''
import logging

import discord
from discord import app_commands
from discord.ext import commands

from variables import VERSION, Config

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
    global CONFG # pylint: disable=global-variable-undefined
    CONFG = Config(bot)
    await bot.add_cog(Utility(bot, Config(bot)))
