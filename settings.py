'''General settings cog.'''
import logging

import discord
from discord import app_commands
from discord.ext import commands

from variables import Config

class Settings(commands.GroupCog, name="settings", description="Settings for the bot."):
    '''Provides commands to change the bot's settings.'''
    def __init__(self, bot: commands.Bot, config: Config):
        self._bt = bot
        self._config = config
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="tracked", description="Change the tracked users.")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def change_tracked(self, ctx: discord.Interaction, user: discord.User):
        """This command is used to change the tracked users.
        If a user is already tracked, they will be untracked."""
        rspns = ctx.response
        wtchd_users = self._config.ticket_users
        if user.id in wtchd_users:
            wtchd_users.remove(user.id)
            await rspns.send_message(f"Untracked {user.mention}", ephemeral=True)
        else:
            wtchd_users.append(user.id)
            await rspns.send_message(f"Tracked {user.mention}", ephemeral=True)
        self._config.ticket_users = wtchd_users

    @app_commands.command(name="staff", description="Change the staff roles.")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def change_staff(self, ctx: discord.Interaction, role: discord.Role):
        """This command is used to change the staff roles, Staff is added to the notes threads.
        If a role is already here, it will be removed."""
        rspns = ctx.response
        stff = self._config.staff
        if role.id in stff:
            stff.remove(role)
            await rspns.send_message(f"Removed {role.mention} from staff roles.", ephemeral=True)
        else:
            stff.append(role)
            await rspns.send_message(f"Added {role.mention} to staff roles.", ephemeral=True)
        self._config.staff = stff

    @app_commands.command(name="staffping", description="Change the staff ping setting.")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def change_staffping(self, ctx: discord.Interaction):
        """This command is used to change the staff ping setting.
        If it is on, it will be turned off, and vice versa."""
        stf_ping = self._config.staff_ping
        self._config.staff_ping = not stf_ping
        await ctx.response.send_message(f"Staff ping is now {not stf_ping}", ephemeral=True)

    @app_commands.command(name="openmsg", description="Change the open message.")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def change_openmsg(self, ctx: discord.Interaction, message: str):
        """This command is used to change the open message."""
        self._config.open_msg = message
        await ctx.response.send_message(f"Open message is now {message}", ephemeral=True)

async def setup(bot: commands.Bot):
    '''Adds the cog to the bot.'''
    await bot.add_cog(Settings(bot, Config(bot)))
