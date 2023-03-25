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
    @commands.guild_only()
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
    @commands.guild_only()
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

    @app_commands.command(name="create", description="Create a tag")
    @commands.guild_only()
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
                     image: Optional[str], thumbnail: Optional[str]) -> None:
        """Creates a tag.

        This command creates a tag, which is a snippet of text that can be
        called up with a command.
        If embed parameters are specified, it creates an embed.

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
            logging.debug("Tag data: %s", tag_data)
            if new:
                await ctx.followup.send("Tag created!", ephemeral=True)
            else:
                raise exceptions.InvalidParameters("That tag already exists!")
            await conn.commit()

    @app_commands.command(name="delete", description="Delete a tag")
    @commands.guild_only()
    @checks.is_staff_check()
    @app_commands.describe(tag="The tag to delete")
    async def delete(self, ctx: discord.Interaction, tag: str) -> None:
        """Deletes a tag.

        This command deletes a tag, which is a snippet of text that can be
        called up with a command.

        Args:
            ctx: The interaction context.
            tag: The tag to delete.

        Raises:
            InvalidParameters: The tag doesn't exist.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            new, tag = await conn.get_tag(ctx.guild_id, tag)  # type: ignore
            if new:
                raise exceptions.InvalidParameters("That tag doesn't exist!")
            await conn.delete(tag)
            await conn.commit()
        emd = discord.Embed(title="Tag deleted!",
                            description=f"Tag `{tag}` deleted!",
                            color=discord.Color.red())
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="edit", description="Edit a tag")
    @commands.guild_only()
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
    async def edit(self, ctx: discord.Interaction, tag_key: str,
                   content: Optional[str], title: Optional[str],
                   url: Optional[str], color: Optional[str],
                   footer: Optional[str], image: Optional[str],
                   thumbnail: Optional[str]) -> None:
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

        Raises:
            InvalidParameters: The tag doesn't exist.
        """
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
            new, tag = await conn.get_tag(ctx.guild_id, tag_key)  # type: ignore
            if new:
                raise exceptions.InvalidParameters("That tag doesn't exist!")
            if content:
                tag.description = content
            if title:
                tag.title = title
            if not tag.title and any(opt_params):
                raise exceptions.InvalidParameters(
                    "You need to specify a title if"
                    " you want to use embed parameters!")
            for param, value in opt_params.items():
                if value:
                    setattr(tag, param, value)
            await conn.commit()
        emd = discord.Embed(title="Tag edited!",
                            description=f"Tag `{tag_key}` edited!",
                            color=discord.Color.green())
        await ctx.response.send_message(embed=emd, ephemeral=True)


async def setup(bot_instance: bot.TicketsPlusBot) -> None:
    """Sets up the tag cog.
    
    Sets the bot to use the cog properly.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(TagUtils(bot_instance))
