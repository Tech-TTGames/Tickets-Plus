"""Miscellaneous commands that don't fit anywhere else.

They are various commands that don't fit into any other category.
They are in free discord commands not assigned to groups.
If the comamnd set warrants it, we may move it to a group.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlusBot(...)
    await bot_instance.load_extension("tickets_plus.cogs.main_utils")
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.

import logging

import discord
from discord import app_commands, utils
from discord.ext import commands

from tickets_plus import bot
from tickets_plus.database import const


class FreeCommands(commands.Cog, name="General Random Commands"):
    """General commands that don't fit anywhere else.

    We assign various commands that don't fit anywhere else to this cog.
    They are in free discord commands not assigned to groups.
    If a context is big enough, we may move it to a group.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot):
        """Initialise the FreeCommands cog.

        We initialise some attributes here for later use.

        Args:
            bot_instance: The bot instance that loaded this cog.
        """
        self._bt = bot_instance
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(
        name="ping",
        description="The classic ping command. Checks the bot's latency.")
    async def ping(self, ctx: discord.Interaction) -> None:
        """The classic ping command. Checks the bot's latency.

        This command is used to check the bot's latency.
        It responds with the bot's latency in milliseconds.

        Args:
            ctx: The interaction context.
        """
        embd = discord.Embed(title="Pong!",
                             description=f"The bot is online.\nPing: "
                             f"{str(round(self._bt.latency * 1000))}ms",
                             color=discord.Color.green())
        await ctx.response.send_message(embed=embd)

    @app_commands.command(name="version", description="Get the bot's version.")
    async def version(self, ctx: discord.Interaction) -> None:
        """This command is used to check the bot's version.

        Responds with the bot's version and a link to the source code.

        Args:
            ctx: The interaction context.
        """
        emd = discord.Embed(
            title="Tickets+",
            description=f"Bot version: {const.VERSION}\n"
            "This bot is open source and experimental!",
            color=discord.Color.from_str("0x00FFFF"),
        ).add_field(
            name="Source Code:",
            value=(
                "[Available on GitHub](https://github.com/Tech-TTGames/Tickets-Plus)"  # pylint: disable=line-too-long # skipcq: PYL-W0511, FLK-W505
                "\nThis is the place to report bugs and suggest features."),
        )
        # .add_field(name="Get Support:",
        #            value="[Join the support server](<NO SUPPORT SERVER YET>)")
        await ctx.response.send_message(embed=emd)

    @app_commands.command(name="invite",
                          description="Invite the bot to a server.")
    async def invite(self, ctx: discord.Interaction) -> None:
        """Invite the bot to a server.

        This command is used to invite the bot to a server.
        It responds with a link to invite the bot to a server.

        Args:
            ctx: The interaction context.
        """
        app = await ctx.client.application_info()
        admn_perms = discord.Permissions(535059492056)
        safe_perms = discord.Permissions(535059492048)
        if app.bot_public:
            emd = discord.Embed(
                title="Tickets+",
                description="Invite the bot to your server with this links:\n",
                color=discord.Color.from_str("0x00FFFF"))
            emd.add_field(
                name="Admin Permissions:",
                value=(
                    f"[Click Here!]({utils.oauth_url(app.id,permissions=admn_perms)})"  # pylint: disable=line-too-long # skipcq: PYL-W0511, FLK-W505
                ),
            )
            emd.add_field(
                name="Safe Permissions:",
                value=(
                    f"[Click Here!]({utils.oauth_url(app.id,permissions=safe_perms)})"  # pylint: disable=line-too-long # skipcq: PYL-W0511, FLK-W505
                ),
            )
        else:
            flg = False
            if app.team:
                # Split to avoid errors ie AttributeError
                if ctx.user in app.team.members:
                    flg = True
            if ctx.user == app.owner:
                flg = True
            if flg:
                emd = discord.Embed(
                    title="Tickets+",
                    description="Welcome back authorised user!\n"
                    "Invite the bot to your server with this link:\n",
                    color=discord.Color.from_str("0x00FFFF"))
                emd.add_field(
                    name="Invite Link:",
                    value=(
                        f"[Click Here!]({utils.oauth_url(app.id,permissions=admn_perms)})"  # pylint: disable=line-too-long # skipcq: PYL-W0511, FLK-W505
                    ),
                )
            else:
                emd = discord.Embed(
                    title="Tickets+",
                    description="Sorry! This instance of the bot is not public."
                    " You can't invite it to your server.",
                    color=discord.Color.red())
        await ctx.response.send_message(embed=emd)


async def setup(bot_instance: bot.TicketsPlusBot) -> None:
    """Sets up up the free commands.

    Called by the bot when the cog is loaded.
    It adds the cog to the bot.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(FreeCommands(bot_instance))
