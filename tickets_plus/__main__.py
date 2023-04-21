#!/usr/bin/env python3
"""A startup file for the tickets_plus bot

We don't really do anything except invoke the start_bot function.
All the magic happens in `tickets_plus`.
This file is to be used as a script, not as a module.

Typical usage example:
    $ python3 tickets_plus
    OR
    $ poetry run start
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import asyncio

import tickets_plus
from tickets_plus.database import statvars


def main():
    """Start the bot

    Adjust the event loop policy if we're on Windows and psycopg3.
    Then, run the bot until it's done.
    """
    print(f"Starting Tickets+ {statvars.VERSION}")
    cnfg = statvars.MiniConfig()
    loop = asyncio.get_event_loop()
    # We don't need to pass the config to start_bot, but we do it anyway
    print("Entering event loop.")
    loop.run_until_complete(tickets_plus.start_bot(cnfg))


if __name__ == "__main__":
    main()
