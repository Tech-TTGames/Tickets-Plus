"""Random commands that don't fit anywhere else."""
import logging

import discord
from discord import app_commands
from discord.ext import commands

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
    await bot.add_cog(FreeCommands(bot))
