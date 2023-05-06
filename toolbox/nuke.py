#!/usr/bin/env python3
"""This script will drop all tables in the database.

This is a destructive operation and should only be used in development.
The tickets_plus schema will also be dropped if it exists.

Typical usage example:
    $ python3 nuke.py
    OR
    $ poetry run nuke
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import asyncio
import pathlib
import sys

from sqlalchemy import schema
from sqlalchemy.ext import asyncio as sa_asyncio

_PROG_DIR = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(_PROG_DIR))

# pylint: disable=wrong-import-position
# pylint: disable=import-error # It works, I promise.
from tickets_plus.database.config import MiniConfig  # isort:skip

_SAFETY_TOGGLE = False
"""A safety toggle to prevent accidental drops."""


def main():
    """An interactive script to drop all tables in the database.

    This is a destructive operation and should only be used in development.
    The tickets_plus schema will also be dropped if it exists.
    Leave the safety toggle enabled unless you know what you're doing.
    Like, really know what you're doing.
    """
    engine = sa_asyncio.create_async_engine(MiniConfig().get_url())
    print("This script will drop all tables in the database."
          " This is a destructive operation and"
          " should only be used in development.")
    print("It will also drop the schema if it exists.")
    inf = input("Do you know what you're doing? (Y/N)\n")
    if inf == "N":
        print("Please consult a developer or system administrator.")
        print("Aborting.")
        return
    op = input("Are you sure you want to drop all tables? (Y/N)\n")
    if op == "Y":
        confrm = input("Are you REALLY sure? (Y/N)\n")
        if confrm == "Y":
            if _SAFETY_TOGGLE:
                asyncio.run(throwaway(engine))
                print("Connection closed. Exiting...")
            else:
                print("Safety toggle not enabled."
                      " Please change the value of"
                      " _SAFETY_TOGGLE to True in nuke.py and try again.")
                print("Aborting.")
        else:
            print("Aborting.")
    else:
        print("Aborting.")


async def throwaway(engine: sa_asyncio.AsyncEngine):
    """Runs everything that needs async.

    This is a throwaway function to run the async stuff.
    """
    print("Safety toggle enabled. Connecting to DB...")
    conn = await engine.connect()
    print("Engine started. Dropping schema...")
    await conn.execute(
        schema.DropSchema("tickets_plus", cascade=True, if_exists=True))
    await conn.commit()
    print("Tables dropped. Closing connection...")
    await conn.close()


if __name__ == "__main__":
    main()
