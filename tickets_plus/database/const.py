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
# If later approved by the Initial Contributor, GPL-3.0-or-later.

import logging.handlers
import pathlib

import discord

VERSION = "v0.2.0.0"
"""The current version of the bot as a string.

FORMAT:
v[major].[minor].[release].[build]

MAJOR and MINOR version changes can be compatibility-breaking.
Compatibility-breaking changes are changes that require manual intervention
by the USER to update the bot. Internal changes that do not require
manual intervention by the USER are not considered compatibility-breaking.
"""
PROG_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
"""The absolute path to the root directory of the bot."""
INTENTS = discord.Intents.default()
"""The discord gateway intents that the bot uses."""
INTENTS.message_content = True
INTENTS.members = True
HANDLER = logging.handlers.RotatingFileHandler(
    filename=pathlib.Path(PROG_DIR, "log", "bot.log"),
    encoding="utf-8",
    mode="w",
    backupCount=10,
    maxBytes=100000,
)
"""The default logging handler for the bot."""
