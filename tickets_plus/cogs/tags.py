"""An extension for all your tagging needs!

This module contains the Tags cog, which allows users to create and manage
tags, which are essentially just snippets of text that can be called up
with a command. Tags can be used by anyone, and can be created by anyone
who has a staff role.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlus(...)
    bot_instance.load_extension("tickets_plus.cogs.tags")
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
import types
from typing import Optional, Tuple

import discord
from discord.ext import commands
from discord import app_commands

from tickets_plus import bot
from tickets_plus.ext import exceptions, checks


@commands.guild_only()
class TagUtils(commands.GroupCog,
               name="tag",
               description="A for all your tagging needs!"):
    """Suitable for all your tagging needs!

    This is the cog responsible for managing tags, which are essentially
    just snippets of text that can be called up with a command. Tags can
    be used by anyone, and can be created by anyone who has a staff role.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot):
        """Initializes the TagUtils cog.

        This method initialises the cog.
        It also sets the bot instance as a private attribute.
        And finally initialises the superclass.

        Args:
            bot_instance: The bot instance.
        """
        self._bt = bot_instance
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    async def prep_tag(
            self, guild: int, tag: str, mention: Optional[discord.User]
    ) -> Tuple[str, None | discord.Embed]:
        """Basic tag preparation.

        Grabs the tag and packages it into a message and embed.
        message also mentions the user if specified.

        Args:
            tag: The tag to send.
            mention: The user to mention.

        Returns:
            A tuple of the message and embed.

        Raises:
            InvalidParameters: The tag doesn't exist.
        """
        async with self._bt.get_connection() as conn:
            emd = None
            tag_data = await conn.fetch_tag(guild, tag)  # type: ignore
            messg = ""
            if mention:
                messg = mention.mention
            if tag_data is None:
                raise exceptions.InvalidParameters("That tag doesn't exist!")
            if isinstance(tag_data, discord.Embed):
                emd = tag_data
            else:
                messg += tag_data
        return messg, emd

    @app_commands.command(name="anosend", description="Send a tag anonymously")
    @app_commands.describe(tag="The tag to send", mention="The user to mention")
    async def anosend(self, ctx: discord.Interaction, tag: str,
                      mention: Optional[discord.User]) -> None:
        """Sends an anonymous tag.

        This command sends an anonymous tag, which is a tag that is sent
        without a connection to the user who sent it.

        Args:
            ctx: The interaction context.
            tag: The tag to send.
            mention: The user to mention.
        """
        await ctx.response.defer(ephemeral=True)
        if isinstance(ctx.channel, (discord.ForumChannel, discord.StageChannel,
                                    discord.CategoryChannel, types.NoneType)):
            raise exceptions.InvalidLocation("You can't use this command here!")
        messg, emd = await self.prep_tag(
            ctx.guild_id,  # type: ignore
            tag,
            mention)
        if emd:
            await ctx.channel.send(content=messg, embed=emd)
        else:
            await ctx.channel.send(messg)
        await ctx.followup.send("Sent!", ephemeral=True)

    @app_commands.command(name="send", description="Send a tag")
    @app_commands.describe(tag="The tag to send", mention="The user to mention")
    async def send(self, ctx: discord.Interaction, tag: str,
                   mention: Optional[discord.User]) -> None:
        """Sends a tag.

        This command sends a tag, which is a snippet of text that can be
        called up with a command.

        Args:
            ctx: The interaction context.
            tag: The tag to send.
            mention: The user to mention.
        """
        await ctx.response.defer(ephemeral=False)
        if isinstance(ctx.channel, (discord.ForumChannel, discord.StageChannel,
                                    discord.CategoryChannel, types.NoneType)):
            raise exceptions.InvalidLocation("You can't use this command here!")
        messg, emd = await self.prep_tag(
            ctx.guild_id,  # type: ignore
            tag,
            mention)
        if emd:
            await ctx.followup.send(content=messg, embed=emd)
        else:
            await ctx.followup.send(messg)

    @app_commands.command(name="create", description="Create/Delete a tag")
    @checks.is_staff_check()
    @app_commands.describe(
        tag="The tag to create",
        content="The content of the tag",
        title="The title of the embed",
        url="The url of the embed",
        color="The color of the embed in hex (e.g. #ff0000)",
        footer="The footer of the embed",
        image="The image of the embed",
        thumbnail="The thumbnail of the embed",
        author="The author of the embed",
    )
    async def create(self, ctx: discord.Interaction, tag: str, content: str,
                     title: Optional[str], url: Optional[str],
                     color: Optional[str], footer: Optional[str],
                     image: Optional[str], thumbnail: Optional[str], author: Optional[str]) -> None:
        """Creates or deletes a tag.

        This command creates a tag, which is a snippet of text that can be
        called up with a command.
        If embed parameters are specified, it creates an embed.
        if the tag already exists, it deletes it.

        Args:
            ctx: The interaction context.
            tag: The tag to create.
            content: The content of the tag.
            title: The title of the embed.
            url: The url of the embed.
            color: The color of the embed.
            footer: The footer of the embed.
            image: The image of the embed.
            thumbnail: The thumbnail of the embed.
            author: The author of the embed.

        Raises:
            InvalidParameters: The tag already exists.
        """
        parsed_color = None
        if (url or color or footer or image or thumbnail) and not title:
            raise exceptions.InvalidParameters(
                "You need to specify a title"
                " if you want to use embed parameters!")
        if color:
            parsed_color = discord.Color.from_str(color).value
        opt_params = {
            "title": title,
            "url": url,
            "color": parsed_color,
            "footer": footer,
            "image": image,
            "thumbnail": thumbnail
        }
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            new, tag_data = await conn.get_tag(
                ctx.guild_id,  # type: ignore
                tag,
                content,
                embed_args=opt_params)
            if new:
                emd = discord.Embed(title="Tag created!",
                                    description=f"Tag `{tag}` created!",
                                    color=discord.Color.green())
            else:
                await conn.delete(tag_data)
                emd = discord.Embed(title="Tag deleted!",
                                    description=f"Tag `{tag}` deleted!",
                                    color=discord.Color.red())
            await conn.commit()
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="edit", description="Edit a tag")
    @checks.is_staff_check()
    @app_commands.describe(
        tag="The tag to edit",
        content="The content of the tag",
        title="The title of the embed",
        url="The url of the embed",
        color="The color of the embed in hex (e.g. #ff0000)",
        footer="The footer of the embed",
        image="The image of the embed",
        thumbnail="The thumbnail of the embed",
        author="The author of the embed",
    )
    async def edit(self, ctx: discord.Interaction, tag: str,
                   content: Optional[str], title: Optional[str],
                   url: Optional[str], color: Optional[str],
                   footer: Optional[str], image: Optional[str],
                   thumbnail: Optional[str], author: Optional[str]) -> None:
        """Edits a tag.

        This command edits a tag, which is a snippet of text that can be
        called up with a command.
        If embed parameters are specified, it edits the embed.

        Args:
            ctx: The interaction context.
            tag: The tag to edit.
            content: The content of the tag.
            title: The title of the embed.
            url: The url of the embed.
            color: The color of the embed.
            footer: The footer of the embed.
            image: The image of the embed.
            thumbnail: The thumbnail of the embed.
            author: The author of the embed.

        Raises:
            InvalidParameters: The tag doesn't exist.
        """
        if not any([content, title, url, color, footer, image, thumbnail]):
            raise exceptions.InvalidParameters(
                "You must specify at least one value to edit.")
        parsed_color = None
        if color:
            parsed_color = discord.Color.from_str(color).value
        opt_params = {
            "url": url,
            "color": parsed_color,
            "footer": footer,
            "image": image,
            "thumbnail": thumbnail
        }
        async with self._bt.get_connection() as conn:
            new, tag_data = await conn.get_tag(ctx.guild_id, tag)  # type: ignore
            if new:
                raise exceptions.InvalidParameters("That tag doesn't exist!")
            if content:
                tag_data.description = content
            if title:
                tag_data.title = title
            if not tag_data.title and any(opt_params):
                raise exceptions.InvalidParameters(
                    "You need to specify a title if"
                    " you want to use embed parameters!")
            for param, value in opt_params.items():
                if value:
                    setattr(tag_data, param, value)
            await conn.commit()
        emd = discord.Embed(title="Tag edited!",
                            description=f"Tag `{tag}` edited!",
                            color=discord.Color.green())
        await ctx.response.send_message(embed=emd, ephemeral=True)


async def setup(bot_instance: bot.TicketsPlusBot) -> None:
    """Sets up the tag cog.

    Sets the bot to use the cog properly.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(TagUtils(bot_instance))
