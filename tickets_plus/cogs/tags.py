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
# If later approved by the Initial Contributor, GPL-3.0-or-later.

import logging
import types
from typing import List, Optional, Tuple

import discord
from discord import app_commands
from discord.ext import commands

from tickets_plus import bot
from tickets_plus.ext import checks, exceptions


@commands.guild_only()
class TagUtils(commands.GroupCog, name="tag", description="A for all your tagging needs!"):
    """Suitable for all your tagging needs!

    This is the cog responsible for managing tags, which are essentially
    just snippets of text that can be called up with a command. Tags can
    be used by anyone, and can be created by anyone who has a staff role.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot):
        """Initializes the TagUtils cog.

        This method initializes the cog.
        It also sets the bot instance as a private attribute.
        And finally initializes the superclass.

        Args:
            bot_instance: The bot instance.
        """
        self._bt = bot_instance
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    async def tag_autocomplete(self, ctx: discord.Interaction, arg: str) -> List[app_commands.Choice[str]]:
        """Autocomplete for tags.

        This method is used to autocomplete tags.
        It gets the tags from the database and returns them as a list of
        choices.

        Args:
            ctx: The interaction context.
            arg: The argument to autocomplete.
        """
        async with self._bt.get_connection() as conn:
            tags = await conn.get_tags(ctx.guild_id)  # type: ignore
        choices = []
        for tag in tags:
            if len(choices) >= 25:
                break
            if arg.lower() in tag.tag_name.lower():
                choices.append(tag.tag_name)
        return choices

    async def prep_tag(self, guild: int, tag: str, mention: Optional[discord.User]) -> Tuple[str, None | discord.Embed]:
        """Basic tag preparation.

        Grabs the tag and packages it into a message and embed.
        The message also mentions the user if specified.

        Args:
            guild: The guild to fetch the tag from.
            tag: The tag to send.
            mention: The user to mention.

        Returns:
            A tuple of the message and embed.

        Raises:
            InvalidParameters: The tag doesn't exist.
        """
        async with self._bt.get_connection() as conn:
            emd = None
            tag_data = await conn.fetch_tag(guild, tag.lower())  # type: ignore
            messg = ""
            if mention:
                messg = f"{mention.mention}\n"
            if tag_data is None:
                raise exceptions.InvalidParameters("That tag doesn't exist!")
            if isinstance(tag_data, discord.Embed):
                emd = tag_data
            else:
                messg += tag_data
        return messg, emd

    @app_commands.command(name="send", description="Send a tag")
    @app_commands.describe(tag="The tag to send", mention="The user to mention", anon="Send anonymously")
    @app_commands.autocomplete(tag=tag_autocomplete)
    async def send(self,
                   ctx: discord.Interaction,
                   tag: str,
                   mention: Optional[discord.User],
                   anon: bool = False) -> None:
        """Sends a tag.

        This command sends a tag, which is a snippet of text that can be
        called up with a command.

        Args:
            ctx: The interaction context.
            tag: The tag to send.
            mention: The user to mention.
            anon: Whether to send anonymously.
        """
        await ctx.response.defer(ephemeral=anon)
        if isinstance(ctx.channel, (
                discord.ForumChannel,
                discord.StageChannel,
                discord.CategoryChannel,
                types.NoneType,
        )):
            raise exceptions.InvalidLocation("You can't use this command here!")
        messg, emd = await self.prep_tag(
            ctx.guild_id,  # type: ignore
            tag,
            mention)
        post = ctx.followup
        if anon:
            post = ctx.channel
        if emd:
            await post.send(content=messg, embed=emd)
        else:
            await post.send(messg)
        await ctx.followup.send("Sent!", ephemeral=True)

    @app_commands.command(name="create", description="Create/Delete a tag")
    @checks.is_staff_check()
    @app_commands.describe(
        tag_name="The tag to create",
        content="The content of the tag",
        title="The title of the embed",
        url="The url of the embed",
        color="The color of the embed in hex (e.g. #ff0000)",
        footer="The footer of the embed",
        image="The image of the embed",
        thumbnail="The thumbnail of the embed",
        author="The author of the embed",
    )
    @app_commands.autocomplete(tag_name=tag_autocomplete)
    async def create(self, ctx: discord.Interaction, tag_name: str, content: str, title: Optional[str],
                     url: Optional[str], color: Optional[str], footer: Optional[str], image: Optional[str],
                     thumbnail: Optional[str], author: Optional[str]) -> None:
        """Creates or deletes a tag.

        This command creates a tag, which is a snippet of text that can be
        called up with a command.
        If embed parameters are specified, it creates an embed.
        If the tag already exists, it deletes it.

        Args:
            ctx: The interaction context.
            tag_name: The tag to create.
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
        await ctx.response.defer(ephemeral=True)
        parsed_color = None
        opt_params = {
            "title": title,
            "url": url,
            "color": parsed_color,
            "footer": footer,
            "image": image,
            "thumbnail": thumbnail,
            "author": author
        }
        if any(opt_params.values()) and not title:
            raise exceptions.InvalidParameters("You need to specify a title"
                                               " if you want to use embed parameters!")
        if color:
            parsed_color = discord.Color.from_str(color).value
        opt_params["color"] = parsed_color
        async with self._bt.get_connection() as conn:
            new, tag_data = await conn.get_tag(
                ctx.guild_id,  # type: ignore
                tag_name.lower(),
                content,
                embed_args=opt_params)
            if new:
                emd = discord.Embed(title="Tag created!",
                                    description=f"Tag `{tag_name}` created!",
                                    color=discord.Color.green())
            else:
                await conn.delete(tag_data)
                emd = discord.Embed(title="Tag deleted!",
                                    description=f"Tag `{tag_name}` deleted!",
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
    @app_commands.autocomplete(tag=tag_autocomplete)
    async def edit(self, ctx: discord.Interaction, tag: str, content: Optional[str], title: Optional[str],
                   url: Optional[str], color: Optional[str], footer: Optional[str], image: Optional[str],
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
        parsed_color = None
        if color:
            parsed_color = discord.Color.from_str(color).value
        opt_params = {
            "url": url,
            "color": parsed_color,
            "footer": footer,
            "image": image,
            "thumbnail": thumbnail,
            "author": author
        }
        async with self._bt.get_connection() as conn:
            new, tag_data = await conn.get_tag(
                ctx.guild_id,  # type: ignore
                tag.lower(),
                "")
            if new:
                raise exceptions.InvalidParameters("That tag doesn't exist!")
            if content:
                tag_data.description = content
            if title:
                tag_data.title = title
            if not tag_data.title and any(opt_params.values()):
                raise exceptions.InvalidParameters("You need to specify a title if"
                                                   " you want to use embed parameters!")
            for param, value in opt_params.items():
                if value:
                    setattr(tag_data, param, value)
            await conn.commit()
        emd = discord.Embed(title="Tag edited!", description=f"Tag `{tag}` edited!", color=discord.Color.green())
        await ctx.response.send_message(embed=emd, ephemeral=True)


async def setup(bot_instance: bot.TicketsPlusBot) -> None:
    """Sets up the tag cog.

    Sets the bot to use the cog properly.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(TagUtils(bot_instance))
