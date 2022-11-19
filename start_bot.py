'''The main bot file. Start the bot.'''
import logging

import discord
from discord.ext import commands

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
    await bot.load_extension("main_utils")
    await bot.load_extension("settings")
    await bot.tree.sync()
    logging.info("Finished loading cogs.")

@bot.tree.command(name="reload", description="Reloads the bot's cogs.")
@commands.is_owner()
async def reload(ctx: discord.Interaction):
    '''Reloads the bot's cogs.'''
    await ctx.response.send_message("Reloading cogs...")
    logging.info("Reloading cogs...")
    await bot.reload_extension("main_utils")
    await bot.reload_extension("settings")
    await ctx.channel.send("Reloaded cogs.") #type: ignore
    logging.info("Finished reloading cogs.")

if __name__ == "__main__":
    bot.run(scrt.token, log_handler=handler, root_logger=True)
