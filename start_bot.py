'''The main bot file. Start the bot.'''
import logging

import discord
from discord.ext import commands

from main_utils import Utility
from variables import Config, VERSION, intents, handler, Secret

bot = commands.Bot(command_prefix='~', intents=intents)
cnfg = Config(bot)
scrt = Secret()

@bot.event
async def on_ready():
    '''Logs bot readiness'''
    logging.info("Connected to Discord as %s", bot.user)
    logging.info("Bot version: %s", VERSION)
    logging.info("Discord.py version: %s", discord.__version__)
    await bot.add_cog(Utility(bot, cnfg))
    await bot.tree.sync()
    logging.info("Finished loading cogs.")

if __name__ == "__main__":
    bot.run(scrt.token, log_handler=handler, root_logger=True)
