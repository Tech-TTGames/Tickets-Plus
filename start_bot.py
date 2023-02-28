"""The main bot file. Start the bot."""
import logging

import discord
from discord.ext import commands

from variables import VERSION, Config, Secret, handler, intents

bot = commands.Bot(command_prefix="~", intents=intents)
cnfg = Config(bot)
if cnfg.msg_discovery:
    intents.message_content = True  # pylint: disable=assigning-non-slot
    intents.messages = True  # pylint: disable=assigning-non-slot
scrt = Secret()


@bot.event
async def on_ready():
    """Logs bot readiness"""
    logging.info("Connected to Discord as %s", bot.user)
    logging.info("Bot version: %s", VERSION)
    logging.info("Discord.py version: %s", discord.__version__)
    await bot.load_extension("main_utils")
    await bot.load_extension("settings")
    await bot.load_extension("override")
    await bot.tree.sync()
    logging.info("Finished loading cogs.")


if __name__ == "__main__":
    bot.run(scrt.token, log_handler=handler, root_logger=True)
