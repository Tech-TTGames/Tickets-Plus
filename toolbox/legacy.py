"""Legacy modules for Tickets+

This module contains the legacy modules that are deprecated in favor of the new
database layer and config modules. They will not be updated. They are only
here for migration purposes.

Typical usage example:
    ```py
    from tickets_plus.database import legacy
    # Make use of the legacy modules
    # This is not recommended, but it is possible
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
import logging
import pathlib
import string
import sys
from typing import Literal

import discord
from discord.ext import commands

_PROG_DIR = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(_PROG_DIR))

# pylint: disable=wrong-import-position
# pylint: disable=import-error # It works, I promise.
# Full disclosure: This is a hacky way to do it.
from tickets_plus.database.const import PROG_DIR  # isort:skip # nopep8

class Config:
    """DEPRECATED. Class for convinient config access"""

    # pylint: disable=line-too-long
    # I'm keeping this class for migration,
    # but it's deprecated and will be removed in the future.
    # Also I'm not going to update the docstrings for this class to the google-style ones.
    # I'm just going to leave them as they are.

    def __init__(self,
                 bot: commands.Bot | Literal["offline"],
                 legacy: bool = False) -> None:
        self._file = pathlib.Path(PROG_DIR, "config.json")
        with open(self._file, encoding="utf-8", mode="r") as config_f:
            self._config: dict = json.load(config_f)
        if not legacy:
            logging.warning("Config is deprecated and read-only."
                            " Use OnlineConfig and MiniConfig instead.")
        self._bot = bot

    def cnfg(self) -> dict:
        """A legacy function to support easier migration to OnlineConfig"""
        return self._config

    @property
    def guild(self) -> discord.Guild:
        """Returns the guild object"""
        if isinstance(self._bot, str):
            raise ValueError("Use online config.")
        gld = self._bot.get_guild(self._config["guild_id"])
        if isinstance(gld, discord.Guild):
            return gld
        raise ValueError("Guild Not Found")

    @property
    def ticket_users(self) -> list[int]:
        """List of users who are tracked for ticket creation"""
        return self._config.get("ticket_users", [508391840525975553])

    @property
    def staff(self) -> list[discord.Role]:
        """List of roles who are staff"""
        staff = []
        for role in self._config.get("staff", []):
            stf_role = self.guild.get_role(role)
            if isinstance(stf_role, discord.Role):
                staff.append(stf_role)
        return staff

    @property
    def staff_ids(self) -> list[int]:
        """List of role ids who are staff"""
        return self._config.get("staff", [])

    @property
    def observers(self) -> list[discord.Role]:
        """List of roles who are pinged in staff notes"""
        staff = []
        for role in self._config.get("observers", []):
            stf_role = self.guild.get_role(role)
            if isinstance(stf_role, discord.Role):
                staff.append(stf_role)
        return staff

    @property
    def open_msg(self) -> string.Template:
        """Returns the message sent when a ticket is opened"""
        return string.Template(
            self._config.get("open_msg", "Staff notes for Ticket $channel."))

    @property
    def staff_team(self) -> str:
        """Returns the staff team name"""
        return self._config.get("staff_team", "Staff Team")

    @property
    def msg_discovery(self) -> bool:
        """Returns if messages should be discovered"""
        return self._config.get("msg_discovery", True)

    @property
    def strip_buttons(self) -> bool:
        """Returns if buttons should be stripped"""
        return self._config.get("strip_buttons", False)

    @property
    def community_roles(self) -> list[discord.Role]:
        """List of roles who are staff"""
        staff = []
        for role in self._config.get("community_roles", []):
            stf_role = self.guild.get_role(role)
            if isinstance(stf_role, discord.Role):
                staff.append(stf_role)
        return staff

    @property
    def community_roles_ids(self) -> list[int]:
        """List of role ids who are staff"""
        return self._config.get("community_roles", [])

    @property
    def owner(self) -> list[int]:
        """List of user ids who are owner"""
        return self._config.get("owner_id", [414075045678284810])