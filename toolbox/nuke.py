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
# Copyright (c) 2021-present The Tickets Plus Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import pathlib
import sys

from sqlalchemy import create_engine, schema

_PROG_DIR = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(_PROG_DIR))

# pylint: disable=wrong-import-position
# pylint: disable=import-error # It works, I promise.
from tickets_plus.database.models import Base  # isort:skip
from tickets_plus.database.statvars import MiniConfig  # isort:skip

_SAFETY_TOGGLE = False
"""A safety toggle to prevent accidental drops."""


def main():
    """An interactive script to drop all tables in the database.

    This is a destructive operation and should only be used in development.
    The tickets_plus schema will also be dropped if it exists.
    Leave the safety toggle enabled unless you know what you're doing.
    Like, really know what you're doing.
    """
    engine = create_engine(MiniConfig().get_url())
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
                print("Safety toggle enabled. Connecting to DB...")
                conn = engine.connect()
                print("Engine started. Dropping schema...")
                conn.execute(
                    schema.DropSchema("tickets_plus",
                                      cascade=True,
                                      if_exists=True))
                print("Schema dropped. Dropping tables...")
                Base.metadata.drop_all(conn)
                print("Tables dropped. Closing connection...")
                conn.close()
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


if __name__ == "__main__":
    main()
