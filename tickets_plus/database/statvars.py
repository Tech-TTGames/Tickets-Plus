"""
Declare variables used in bot.
This file is a based on the variables.py file from my other bot.
"""
import json
import logging
import pathlib
from logging.handlers import RotatingFileHandler
from string import Template
from typing import Any, List, Literal, Union

import discord
from discord.ext import commands
from sqlalchemy import URL

# v[major].[minor].[release].[build]
# MAJOR and MINOR version changes can be compatibility-breaking
VERSION = "v0.1.0.0"
PROG_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()

intents = discord.Intents.default()
handler = RotatingFileHandler(
    filename=pathlib.Path(PROG_DIR, "log", "discord.log"),
    encoding="utf-8",
    mode="w",
    backupCount=10,
    maxBytes=100000,
)


class Secret:
    """Class for secret.json management"""

    def __init__(self) -> None:
        self._file = pathlib.Path(PROG_DIR, "secret.json")
        with open(self._file, encoding="utf-8", mode="r") as secret_f:
            self.secrets = json.load(secret_f)
        self.token = self.secrets["token"]

    def __repr__(self) -> str:
        return "[OBFUSCATED]"

    def __str__(self) -> str:
        return "[OBFUSCATED]"


class MiniConfig:
    """Class for new config.json management"""

    def __init__(self) -> None:
        self._file = pathlib.Path(PROG_DIR, "config.json")
        with open(self._file, encoding="utf-8", mode="r") as config_f:
            self._config: dict = json.load(config_f)

    def __dict__(self) -> dict:
        return self._config

    def getitem(self, key: str, opt: Any = None) -> Any:
        return self._config.get(key, opt)

    def get_url(self) -> URL:
        return URL.create(
            drivername=self._config["dbtype"],
            host=self._config["dbhost"],
            port=self._config["dbport"],
            username=self._config["dbuser"],
            password=self._config["dbpass"],
            database=self._config["dbname"],
        )


class Config:
    """DEPRECATED. Class for convinient config access"""

    def __init__(self, bot: Union[commands.Bot, Literal["offline"]]) -> None:
        self._file = pathlib.Path(PROG_DIR, "config.json")
        with open(self._file, encoding="utf-8", mode="r") as config_f:
            self._config: dict = json.load(config_f)
        logging.warning(
            "Config is deprecated and read-only. Use OnlineConfig and MiniConfig instead."
        )
        self._bot = bot

    def __dict__(self) -> dict:
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
    def ticket_users(self) -> List[int]:
        """List of users who are tracked for ticket creation"""
        return self._config.get("ticket_users", [508391840525975553])

    @property
    def staff(self) -> List[discord.Role]:
        """List of roles who are staff"""
        staff = []
        for role in self._config.get("staff", []):
            stf_role = self.guild.get_role(role)
            if isinstance(stf_role, discord.Role):
                staff.append(stf_role)
        return staff

    @property
    def staff_ids(self) -> List[int]:
        """List of role ids who are staff"""
        return self._config.get("staff", [])

    @property
    def observers(self) -> List[discord.Role]:
        """List of roles who are pinged in staff notes"""
        staff = []
        for role in self._config.get("observers", []):
            stf_role = self.guild.get_role(role)
            if isinstance(stf_role, discord.Role):
                staff.append(stf_role)
        return staff

    @property
    def open_msg(self) -> Template:
        """Returns the message sent when a ticket is opened"""
        return Template(
            self._config.get("open_msg", "Staff notes for Ticket $channel.")
        )

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
    def community_roles(self) -> List[discord.Role]:
        """List of roles who are staff"""
        staff = []
        for role in self._config.get("community_roles", []):
            stf_role = self.guild.get_role(role)
            if isinstance(stf_role, discord.Role):
                staff.append(stf_role)
        return staff

    @property
    def community_roles_ids(self) -> List[int]:
        """List of role ids who are staff"""
        return self._config.get("community_roles", [])

    @property
    def owner(self) -> List[int]:
        """List of user ids who are owner"""
        return self._config.get("owner_id", [414075045678284810])
