"""General settings cog."""
import logging

import discord
from discord import app_commands
from discord.ext import commands

from extchecks import is_owner
from variables import Config


class Settings(commands.GroupCog, name="settings", description="Settings for the bot."):
    """Provides commands to change the bot's settings."""

    def __init__(self, bot: commands.Bot, config: Config):
        self._bt = bot
        self._config = config
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="tracked", description="Change the tracked users.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def change_tracked(self, ctx: discord.Interaction, user: discord.User):
        """
        This command is used to change the tracked users.
        If a user is already tracked, they will be untracked.
        """
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
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def change_staff(self, ctx: discord.Interaction, role: discord.Role):
        """
        This command is used to change the staff roles, Staff is added to the notes threads.
        If a role is already here, it will be removed.
        """
        rspns = ctx.response
        stff = self._config.staff
        if role in stff:
            stff.remove(role)
            await rspns.send_message(
                f"Removed {role.mention} from staff roles.", ephemeral=True
            )
        else:
            stff.append(role)
            await rspns.send_message(
                f"Added {role.mention} to staff roles.", ephemeral=True
            )
        self._config.staff = stff

    @app_commands.command(
        name="staffping", description="Change the staff ping setting."
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def change_staffping(self, ctx: discord.Interaction):
        """
        This command is used to change the staff ping setting.
        If it is on, it will be turned off, and vice versa.
        """
        stf_ping = self._config.staff_ping
        self._config.staff_ping = not stf_ping
        await ctx.response.send_message(
            f"Staff ping is now {not stf_ping}", ephemeral=True
        )

    @app_commands.command(name="openmsg", description="Change the open message.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def change_openmsg(self, ctx: discord.Interaction, message: str):
        """This command is used to change the open message."""
        self._config.open_msg = message
        await ctx.response.send_message(
            f"Open message is now {message}", ephemeral=True
        )

    @app_commands.command(name="staffteam", description="Change the staff team's name.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def change_staffteam(self, ctx: discord.Interaction, name: str):
        """This command is used to change the staff team's name."""
        self._config.staff_team = name
        await ctx.response.send_message(f"Staff team is now {name}", ephemeral=True)

    @app_commands.command(
        name="msgdiscovery", description="Toggle message link discovery."
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def toggle_msg_discovery(self, ctx: discord.Interaction):
        """This command is used to toggle message link discovery."""
        self._config.msg_discovery = not self._config.msg_discovery
        await ctx.response.send_message(
            f"Message link discovery is now {self._config.msg_discovery}",
            ephemeral=True,
        )

    @app_commands.command(name="stripbuttons", description="Toggle button stripping.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def toggle_button_stripping(self, ctx: discord.Interaction):
        """This command is used to toggle button stripping."""
        self._config.strip_buttons = not self._config.strip_buttons
        await ctx.response.send_message(
            f"Button stripping is now {self._config.strip_buttons}", ephemeral=True
        )

    @app_commands.command(
        name="communitysupport", description="Change the community support roles."
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def change_community_roles(
        self, ctx: discord.Interaction, role: discord.Role):
        """
        This command is used to change the community support roles,
        COMSUP roles are added to channels side-by-side without any perms.
        If a role is already here, it will be removed.
        """
        rspns = ctx.response
        comsup = self._config.community_roles
        if role in comsup:
            comsup.remove(role)
            await rspns.send_message(
                f"Removed {role.mention} from community support roles.", ephemeral=True
            )
        else:
            comsup.append(role)
            await rspns.send_message(
                f"Added {role.mention} to community support roles.", ephemeral=True
            )
        self._config.community_roles = comsup

    @app_commands.command(name="guild", description="Change the guild.")
    @app_commands.check(is_owner)
    @app_commands.guild_only()
    async def change_guild(self, ctx: discord.Interaction):
        """This command is used to change the guild. Use in the guild you want to change to."""
        if ctx.guild is None:
            await ctx.response.send_message(
                "You must be in a guild to use this command.", ephemeral=True
            )
            return
        self._config.guild = ctx.guild
        await ctx.response.send_message(
            f"Guild is now {ctx.guild.name}", ephemeral=True
        )

    @app_commands.command(name="owner", description="Change the owners of the bot.")
    @app_commands.check(is_owner)
    async def change_owner(self, ctx: discord.Interaction, user: discord.User):
        """
        This command is used to change the owner users.
        If a user is already owner, they will be not be removed.
        """
        rspns = ctx.response
        owner_users = self._config.owner
        owner_users.append(user.id)
        await rspns.send_message(
            f"Added {user.mention} as admin. To remove edit config,json.",
            ephemeral=True,
        )
        self._config.owner = owner_users


async def setup(bot: commands.Bot):
    """Adds the cog to the bot."""
    await bot.add_cog(Settings(bot, Config(bot)))
