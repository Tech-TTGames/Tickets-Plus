#!/usr/bin/env python3
"""
This script will drop all tables in the database.
This is a destructive operation and should only be used in development.
It will also drop the schema if it exists.
"""
# License: EPL-2.0
# Copyright (c) 2021-present The Tickets Plus Contributors
import pathlib
import sys

from sqlalchemy import create_engine, schema

PROG_DIR = pathlib.Path(__file__).parent.parent.absolute()
print(PROG_DIR)
sys.path.append(str(PROG_DIR))

# pylint: disable=wrong-import-position
# pylint: disable=import-error # It works, I promise.
from tickets_plus.database.models import Base  # isort:skip
from tickets_plus.database.statvars import MiniConfig  # isort:skip

SAFETY_TOGGLE = False


def main():
    engine = create_engine(MiniConfig().get_url())
    print(
        "This script will drop all tables in the database."
        " This is a destructive operation and should only be used in development."
    )
    print("It will also drop the schema if it exists.")
    op = input("Are you sure you want to drop all tables? (Y/N)\n")
    if op == "Y":
        confrm = input("Are you REALLY sure? (Y/N)\n")
        if confrm == "Y":
            if SAFETY_TOGGLE:
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
                print(
                    "Safety toggle not enabled."
                    " Please change the value of SAFETY_TOGGLE to True in nuke.py and try again."
                )
                print("Aborting.")
        else:
            print("Aborting.")
    else:
        print("Aborting.")


if __name__ == "__main__":
    main()
