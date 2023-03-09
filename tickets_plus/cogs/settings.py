"""General settings cog."""
import logging

import discord
from discord import app_commands
from discord.ext import commands

from tickets_plus import TicketsPlus


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Settings(commands.GroupCog, name="settings", description="Settings for the bot."):
    """Provides commands to change the bot's settings."""

    def __init__(self, bot: TicketsPlus):
        self._bt = bot
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="tracked", description="Change the tracked users.")
    @app_commands.describe(user="The user to track/untrack.")
    async def change_tracked(self, ctx: discord.Interaction, user: discord.User):
        """
        This command is used to change the tracked users.
        If a user is already tracked, they will be untracked.
        """
        if ctx.guild is None:
            await ctx.response.send_message("This command can only be used in a guild.")
            return
        async with self._bt.get_connection() as conn:
            rspns = ctx.response
            new, ticket_user = await conn.get_ticket_user(user.id, ctx.guild.id, False)
            if not new:
                await conn.delete(ticket_user)
                await rspns.send_message(f"Untracked {user.mention}", ephemeral=True)
            else:
                await rspns.send_message(f"Tracked {user.mention}", ephemeral=True)
            await conn.commit()
            await conn.close()

    @app_commands.command(name="staff", description="Change the staff roles.")
    @app_commands.describe(role="The role to add/remove from staff roles.")
    async def change_staff(self, ctx: discord.Interaction, role: discord.Role):
        """
        This command is used to change the staff roles, Staff are allowed to use staff commands.
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

    @app_commands.command(name="observers", description="Change the observers roles.")
    @app_commands.describe(role="The role to add/remove from observers roles.")
    async def change_observers(self, ctx: discord.Interaction, role: discord.Role):
        """
        This command is used to change the observers roles, which are pinged one new notes threads.
        If a role is already here, it will be removed.
        """
        rspns = ctx.response
        obsrvrs = self._config.observers
        if role in obsrvrs:
            obsrvrs.remove(role)
            await rspns.send_message(
                f"Removed {role.mention} from ping staff roles.", ephemeral=True
            )
        else:
            obsrvrs.append(role)
            await rspns.send_message(
                f"Added {role.mention} to ping staff roles.", ephemeral=True
            )
        self._config.observers = obsrvrs

    @app_commands.command(name="openmsg", description="Change the open message.")
    @app_commands.describe(message="The new open message.")
    async def change_openmsg(self, ctx: discord.Interaction, message: str):
        """This command is used to change the open message."""
        self._config.open_msg = message
        await ctx.response.send_message(
            f"Open message is now {message}", ephemeral=True
        )

    @app_commands.command(name="staffteam", description="Change the staff team's name.")
    @app_commands.describe(name="The new staff team's name.")
    async def change_staffteam(self, ctx: discord.Interaction, name: str):
        """This command is used to change the staff team's name."""
        self._config.staff_team = name
        await ctx.response.send_message(f"Staff team is now {name}", ephemeral=True)

    @app_commands.command(
        name="msgdiscovery", description="Toggle message link discovery."
    )
    async def toggle_msg_discovery(self, ctx: discord.Interaction):
        """This command is used to toggle message link discovery."""
        self._config.msg_discovery = not self._config.msg_discovery
        await ctx.response.send_message(
            f"Message link discovery is now {self._config.msg_discovery}",
            ephemeral=True,
        )

    @app_commands.command(name="stripbuttons", description="Toggle button stripping.")
    async def toggle_button_stripping(self, ctx: discord.Interaction):
        """This command is used to toggle button stripping."""
        self._config.strip_buttons = not self._config.strip_buttons
        await ctx.response.send_message(
            f"Button stripping is now {self._config.strip_buttons}", ephemeral=True
        )

    @app_commands.command(
        name="communitysupport", description="Change the community support roles."
    )
    @app_commands.describe(role="The role to add/remove from community support roles.")
    async def change_community_roles(
        self, ctx: discord.Interaction, role: discord.Role
    ):
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


async def setup(bot: TicketsPlus):
    """Setup function for the cog."""
    await bot.add_cog(Settings(bot))
