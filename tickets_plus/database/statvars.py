"""Constant variables used throughout the bot.

We use this file to store static variables that are used throughout the bot.
This is to keep the code clean and easy to read.
We also use this file to store the bot's version number.
Basically, this file is a collection of global constants.

Typical usage example:
    ```py
    from tickets_plus.database import statvars
    # Make use of the variables in this file
    print(statvars.VERSION)
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
from logging import handlers
from typing import TYPE_CHECKING, Any, Literal

import discord
import sqlalchemy
from discord.ext import commands

VERSION = "v0.1.0.0"
"""The current version of the bot as a string.

FORMAT:
v[major].[minor].[release].[build]

MAJOR and MINOR version changes can be compatibility-breaking.
"""
PROG_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
"""The absolute path to the root directory of the bot."""
INTENTS = discord.Intents.default()
"""The discord gateway intents that the bot uses."""
INTENTS.members = True
HANDLER = handlers.RotatingFileHandler(
    filename=pathlib.Path(PROG_DIR, "log", "bot.log"),
    encoding="utf-8",
    mode="w",
    backupCount=10,
    maxBytes=100000,
)
"""The default logging handler for the bot."""


class Secret:
    """Class for secret.json management

    This class is used to manage the secret.json file.
    It is used to store sensitive information such as the bot token.
    This class is used to obfuscate the token when printing the object.
    Also, this class is used to make it easier to access the token.

    Attributes:
        token: The bot token.
        secrets: The raw dictionary of the secret.json file.
    """

    token: str
    secrets: dict[str, Any]

    def __init__(self) -> None:
        """Loads the secret.json file and stores the data in self.secrets

        We load the secret.json file and store the data in self.secrets.
        We also store the token in self.token for easy access.
        """
        self._file = pathlib.Path(PROG_DIR, "secret.json")
        if not TYPE_CHECKING:
            with open(self._file, encoding="utf-8", mode="r") as secret_f:
                self.secrets = json.load(secret_f)
            self.token: str = self.secrets["token"]
        else:
            self.secrets = {}
            self.token = ""

    def __repr__(self) -> str:
        return "[OBFUSCATED]"

    def __str__(self) -> str:
        return "[OBFUSCATED]"


class MiniConfig:
    """Class for new config.json management

    This class is used to manage the config.json file.
    It is used to store non-sensitive information such as the bot prefix.
    It does not allow for modification of the config.json file.
    As any functiality that should modify the config.json file should be
    instead implemented in the `tickets_plus.database.layer.OnlineConfig` class.
    """

    def __init__(self) -> None:
        self._file = pathlib.Path(PROG_DIR, "config.json")
        if not TYPE_CHECKING:
            with open(self._file, encoding="utf-8", mode="r") as config_f:
                self._config: dict = json.load(config_f)
        else:
            self._config: dict = {}

    def __dict__(self) -> dict:
        return self._config

    def getitem(self, key: str, opt: Any = None) -> Any:
        """Returns the value of a key in the config.json file

        Args:
          key: The key to get the value of
          opt: The default value to return if the key is not found

        Returns:
          Any: The value of the key in the config.json file
            or the default value if the key is not found.
        """
        return self._config.get(key, opt)

    def get_url(self) -> sqlalchemy.URL:
        """Returns the database URL

        Returns:
            `sqlalchemy.URL`: The database URL as a sqlalchemy URL object
        """
        return sqlalchemy.URL.create(
            drivername=self._config["dbtype"],
            host=self._config["dbhost"],
            port=self._config["dbport"],
            username=self._config["dbuser"],
            password=self._config["dbpass"],
            database=self._config["dbname"],
        )


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
