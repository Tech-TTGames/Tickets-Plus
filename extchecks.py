from typing import Optional

import discord
from discord.ext import commands

from variables import Config

CONFG = Config('offline')

def is_owner(interaction: discord.Interaction):
    return interaction.user.id in CONFG.owner
