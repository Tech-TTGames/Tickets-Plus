"""General owner utility commands."""
import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from extchecks import is_owner_gen
from variables import PROG_DIR, Config

IS_OWNER = is_owner_gen()

class Overrides(
    commands.GroupCog, name="override", description="Owner override commands."
):
    """Owner override commands."""

    def __init__(self, bot: commands.Bot, config: Config):
        self._bt = bot
        self._config = config
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="reload", description="Reloads the bot's cogs.")
    @app_commands.check(IS_OWNER)
    async def reload(self, ctx: discord.Interaction):
        """Reloads the bot's cogs."""
        await ctx.response.send_message("Reloading cogs...")
        logging.info("Reloading cogs...")
        await self._bt.reload_extension("main_utils")
        await self._bt.reload_extension("settings")
        await self._bt.reload_extension("override")
        await ctx.channel.send("Reloaded cogs.")  # type: ignore
        logging.info("Finished reloading cogs.")
        await self._bt.tree.sync()
        logging.info("Finished syncing tree.")

    @app_commands.command(name="restart", description="Restarts the bot.")
    @app_commands.check(IS_OWNER)
    async def restart(self, ctx: discord.Interaction):
        """Restarts the bot."""
        await ctx.response.send_message("Restarting...")
        logging.info("Restarting...")
        await self._bt.close()

    @app_commands.command(
        name="pull", description="Pulls the latest changes from the git repo."
    )
    @app_commands.check(IS_OWNER)
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
    @app_commands.check(IS_OWNER)
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

    @app_commands.command(name="config", description="Sends the config.")
    @app_commands.check(IS_OWNER)
    async def config(self, ctx: discord.Interaction):
        """Sends the config."""
        await ctx.response.defer(thinking=True)
        logging.info("Sending config to %s...", str(ctx.user))
        file_path = os.path.join(PROG_DIR, "config.json")
        try:
            await ctx.user.send(file=discord.File(fp=file_path))
        except FileNotFoundError:
            await ctx.followup.send("Config not found.")
            logging.info("Config not found.")
            return
        await ctx.followup.send("Sent config.")
        logging.info("Config sent.")

    @app_commands.command(name="dumpconfig", description="Deletes all data from config")
    @app_commands.check(IS_OWNER)
    async def dump_config(self, ctx: discord.Interaction, confirm: bool):
        """Dump config of bot"""
        if confirm:
            self._config.dump()
            await ctx.response.send_message(
                "Configuration dumped.\n**Prepare for unforeseen consequences.**"
            )
            return
        await ctx.response.send_message("Dump aborted.")


async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    global IS_OWNER # pylint: disable=global-statement
    IS_OWNER = is_owner_gen(getattr(bot, "config"))
    await bot.add_cog(Overrides(bot, getattr(bot, "config")))
