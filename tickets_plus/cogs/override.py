"""General owner utility commands."""
import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from tickets_plus.bot import TicketsPlus
from tickets_plus.cogs import EXTENSIONS
from tickets_plus.database.statvars import PROG_DIR, MiniConfig
from tickets_plus.ext.checks import is_owner_check

CNFG = MiniConfig()


@app_commands.guilds(CNFG.getitem("dev_guild_id"))
class Overrides(
    commands.GroupCog, name="override", description="Owner override commands."
):
    """Owner override commands."""

    def __init__(self, bot: TicketsPlus):
        self._bt = bot
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="reload", description="Reloads the bot's cogs.")
    @is_owner_check()
    @app_commands.describe(sync="Syncs the tree after reloading cogs.")
    async def reload(self, ctx: discord.Interaction, sync: bool = False):
        """Reloads the bot's cogs."""
        await ctx.response.send_message("Reloading cogs...")
        logging.info("Reloading cogs...")
        for extension in EXTENSIONS:
            await self._bt.reload_extension(extension)
        await ctx.channel.send("Reloaded cogs.")  # type: ignore
        logging.info("Finished reloading cogs.")
        if sync:
            await self._bt.tree.sync()
            logging.info("Finished syncing tree.")

    @app_commands.command(name="restart", description="Restarts the bot.")
    @is_owner_check()
    async def restart(self, ctx: discord.Interaction):
        """Restarts the bot."""
        await ctx.response.send_message("Restarting...")
        logging.info("Restarting...")
        await self._bt.close()

    @app_commands.command(
        name="pull", description="Pulls the latest changes from the git repo."
    )
    @is_owner_check()
    async def pull(self, ctx: discord.Interaction):
        """Pulls the latest changes from the git repo."""
        await ctx.response.send_message("Pulling latest changes...")
        logging.info("Pulling latest changes...")
        pull = await asyncio.create_subprocess_shell(
            "git pull",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PROG_DIR,
        )
        stdo, stdr = await pull.communicate()
        if stdo:
            await ctx.followup.send(f"[stdout]\n{stdo.decode()}")
            logging.info("[stdout]\n%s", stdo.decode())

        if stdr:
            await ctx.followup.send(f"[stderr]\n{stdr.decode()}")
            logging.info("[stderr]\n%s", stdr.decode())

        await ctx.followup.send(
            "Finished pulling latest changes.\n"
            "Restart bot or reload cogs to apply changes."
        )

    @app_commands.command(name="logs", description="Sends the logs.")
    @is_owner_check()
    @app_commands.describe(id_no="Log ID (0 for latest log)")
    async def logs(self, ctx: discord.Interaction, id_no: int = 0):
        """Sends the logs."""
        await ctx.response.defer(thinking=True)
        logging.info("Sending logs to %s...", str(ctx.user))
        filename = f"discord.log{'.'+str(id_no) if id_no else ''}"
        file_path = os.path.join(PROG_DIR, "log", filename)
        try:
            await ctx.user.send(file=discord.File(fp=file_path))
        except FileNotFoundError:
            await ctx.followup.send("Specified log not found.")
            logging.info("Specified log not found.")
            return
        await ctx.followup.send("Sent logs.")
        logging.info("Logs sent.")

    @app_commands.command(name="config", description="Sends the guild config.")
    @is_owner_check()
    @app_commands.describe(guid="Guild ID")
    async def config(self, ctx: discord.Interaction, guid: int):
        """Sends the config."""
        await ctx.response.defer(thinking=True)
        logging.info("Sending config to %s...", str(ctx.user))
        async with self._bt.get_connection() as conn:
            guild_confg = await conn.get_guild(guid)
            await ctx.user.send(str(guild_confg))  # Eh. This is a bit of a test.
            await conn.close()
        await ctx.followup.send("Sent config.")
        logging.info("Config sent.")

    @commands.command(name="sync", description="Syncs the tree.")
    @is_owner_check()
    async def sync(self, ctx: commands.Context):
        """Syncs the tree."""
        await ctx.send("Syncing...")
        logging.info("Syncing...")
        await self._bt.tree.sync()
        await ctx.send("Synced.")
        logging.info("Synced.")


async def setup(bot: TicketsPlus):
    """Setup function for the cog."""
    await bot.add_cog(Overrides(bot))
