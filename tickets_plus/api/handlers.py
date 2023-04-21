"""Application Interface Handlers.

This module contains the handlers for the application interface.
As it stands, these are not for use by the end user, but rather
can be used by the main bot to deliver ticket data to our app.
Not to be used directly, but rather through the routes module.

Typical usage example:
    ```py
    from tickets_plus.api import handlers

    ...
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.

import json

import discord
from tornado import web
from sqlalchemy import orm

from tickets_plus import bot
from tickets_plus.cogs import events
from tickets_plus.database import models


class BotHandler(web.RequestHandler):
    """Handler for the bot to send data to the app.

    This handler is used to recive data into the bot
    """

    def initialize(self, bot_instance: bot.TicketsPlusBot) -> None:
        """Initialize the handler.

        Initialize the handler with the bot object.

        Args:
            bot_instance: The bot object.
        """
        self._bt = bot_instance
        self.SUPPORTED_METHODS = ("POST",)  # pylint: disable=invalid-name

    def set_default_headers(self) -> None:
        """Sets the return type to JSON.

        Not striclty necessary, but it's good practice.
        """
        self.set_header("Content-Type", "application/json")

    # pylint: disable=invalid-overridden-method
    async def prepare(self) -> None:
        """Prepare the handler.

        Check if the request is authorized.
        """
        if self.request.body == b"":
            self.set_status(400, "No data provided.")
            self.write({"error": "No data provided."})
            self.finish()
            return
        if self.request.headers.get("ticketsplus-api-auth") is None:
            self.set_status(401, "No authentication token provided.")
            self.write({"error": "No authentication token provided."})
            self.finish()
            return
        if self.request.headers.get(
                "ticketsplus-api-auth") != self._bt.stat_confg.getitem(
                    "auth_token"):
            self.set_status(401, "Invalid authentication token.")
            self.write({"error": "Invalid authentication token."})
            self.finish()
            return
        if self.request.headers.get("Content-Type") is None:
            self.set_status(400, "No Content-Type header provided.")
            self.write({"error": "No Content-Type header provided."})
            self.finish()
            return
        if self.request.headers.get("Content-Type") == "application/json":
            self.args = json.loads(self.request.body.decode("utf-8"))
            await self._bt.wait_until_ready()
            return
        self.set_status(400, "Invalid Content-Type header provided.")
        self.write({"error": "Invalid Content-Type header provided."})
        self.finish()


class TicketHandler(BotHandler):
    """Handles integration-based ticket creation.

    The integration-based version of
    `tickets_plus.cogs.events.on_channel_create`.
    Does the same thing, but also parses the data from the
    request.
    """

    async def post(self) -> None:
        """Handle the request.

        Handle the request and create the ticket.
        Parses the POST data.

        Args:
            guild_id (str): The discord ID of the guild.
            user_id (str): The user ID of the user.
            ticket_channel_id (str): The ID of the channel
        """
        async with self._bt.get_connection() as db:
            try:
                guild_id = int(self.args["guild_id"])
                user_id = int(self.args["user_id"])
                ticket_channel_id = int(self.args["ticket_channel_id"])
            except (ValueError, KeyError):
                self.set_status(400, "Missing or invalid parameters.")
                self.write({"error": "Missing or invalid parameters."})
                self.finish()
                return
            guild = self._bt.get_guild(guild_id)
            if guild is None:
                self.set_status(404, "Guild not found.")
                self.write({"error": "Guild not found."})
                self.finish()
                return
            gld = await db.get_guild(
                guild_id,
                (
                    orm.selectinload(models.Guild.observers_roles),
                    orm.selectinload(models.Guild.community_roles),
                    orm.selectinload(models.Guild.community_pings),
                ),
            )
            if not gld.integrated:
                self.set_status(409, "Guild not integrated.")
                self.write({"error": "Guild not integrated."})
                self.finish()
                return
            channel = guild.get_channel(ticket_channel_id)
            if channel is None or not isinstance(channel, discord.TextChannel):
                self.set_status(404, "Channel not found.")
                self.write({"error": "Channel not found."})
                self.finish()
                return
            user = self._bt.get_user(user_id)
            await events.Events.ticket_creation(self, db, (guild, gld), channel,
                                                user)
            self.set_status(200, "OK")
            self.finish()


class OverrideHandler(BotHandler):
    """Basic messaging capabilites with the bot

    Handles override messages being sent.
    """

    async def post(self):
        """Handles override attempt.

        Tries to meet the parameters specified in the attempt.

        Args:
            guild_id (str): The ID of the guild.
            channel_id (str): The ID of the channel.
            message (str): The message to send.
        """
        try:
            guild_id = int(self.args["guild_id"])
            channel_id = int(self.args["channel_id"])
            message = self.args["message"]
        except (ValueError, KeyError):
            self.set_status(400, "Missing or invalid parameters.")
            self.finish()
            return
        guild = self._bt.get_guild(guild_id)
        if guild is None:
            self.set_status(404, "Guild not found.")
            self.finish()
            return
        channel = guild.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            self.set_status(404, "Channel not found.")
            self.finish()
            return
        await channel.send(message)
        self.set_status(200, "OK")
        self.finish()
