"""Module for .json file management.

This module is used to manage the .json files used by the bot.
Those are: config.json, secret.json, and runtimeconfig.json.
The config.json file stores basic configuration information.
The secret.json file stores sensitive information such as the bot token, etc.
The runtimeconfig.json file stores advanced configuration information, it is
not meant to be edited by less experienced users. Wrong values in this file
may cause issues with the bot and/or discord API.

Typical usage example:
    ```py
    from tickets_plus.database import config
    # Make use of the config module
    # i.e., import and use the Classes
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contributor, GPL-3.0-or-later.

import json
import logging
import pathlib
from typing import Any

import sqlalchemy

from tickets_plus.database import const


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
        """Loads the secret.json file and stores the data in `self.secrets`

        We load the secret.json file and store the data in self.secrets.
        We also store the token in `self.token` for easy access.
        """
        self._file = pathlib.Path(const.PROG_DIR, "secret.json")
        try:
            with open(self._file, encoding="utf-8") as secret_f:
                self.secrets = json.load(secret_f)
            self.token: str = self.secrets["token"]
            self.ssl_key: str = self.secrets["ssl_key"]
        except FileNotFoundError:
            logging.warning("Running in dry-run mode.")
            self._file = pathlib.Path(const.PROG_DIR, "example_secret.json")
            with open(self._file, encoding="utf-8") as secret_f:
                self.secrets = json.load(secret_f)
            self.token: str = self.secrets["token"]
            self.ssl_key: str = self.secrets["ssl_key"]

    def __repr__(self) -> str:
        return "[OBFUSCATED]"

    def __str__(self) -> str:
        return "[OBFUSCATED]"


class MiniConfig:
    """Class for new config.json management

    This class is used to manage the config.json file.
    It is used to store non-sensitive information such as the bot prefix.
    It does not allow for modification of the config.json file.
    As any functionality that should modify the config.json file should be
    instead implemented in the `tickets_plus.database.layer.OnlineConfig` class.
    """

    def __init__(self) -> None:
        self._file = pathlib.Path(const.PROG_DIR, "config.json")
        try:
            with open(self._file, encoding="utf-8") as config_f:
                self._config: dict = json.load(config_f)
        except FileNotFoundError:
            logging.warning("Running in dry-run mode.")
            self._file = pathlib.Path(const.PROG_DIR, "example_config.json")
            with open(self._file, encoding="utf-8") as config_f:
                self._config: dict = json.load(config_f)

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


class RuntimeConfig:
    """Advanced low-level configuration parameters

    This class is used to manage the runtimeconfig.json file.
    It is used to store advanced configuration information.
    It is not meant to be edited by less experienced users.

    Parameters:
        spt_clean_usr: Clean user roles seconds per tick
        spt_notif_usr: Notify user seconds per tick
    """

    def __init__(self) -> None:
        self._file = pathlib.Path(const.PROG_DIR, "runtimeconfig.json")
        with open(self._file, encoding="utf-8") as config_f:
            self._config: dict = json.load(config_f)

    def __dict__(self) -> dict:
        return self._config

    @property
    def spt_clean_usr(self) -> int:
        """Returns the clean user roles seconds per tick

        Returns:
            int: The clean user roles seconds per tick
        """
        return self._config["spt"]["clean_usr"]

    @property
    def spt_notif_usr(self) -> int:
        """Returns the notify user seconds per tick

        Returns:
            int: The notify user seconds per tick
        """
        return self._config["spt"]["notif_usr"]
