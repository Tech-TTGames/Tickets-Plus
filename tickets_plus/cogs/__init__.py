"""A import utility for loading all cogs in this directory.

This file just makes it easier to load all cogs in this directory.
It is not meant to be used as a script.

Example:
    ```py
    from tickets_plus import cogs
    for extension in cogs.EXTENSIONS:
        await bot.load_extension(extension)
    ```
"""
# License: EPL-2.0
# Copyright (c) 2021-2023 The Tickets Plus Contributors
import pkgutil

EXTENSIONS = [
    module.name for module in pkgutil.iter_modules(__path__, f"{__package__}.")
]
"""A list of all cogs in this directory. This is the list of cogs to load."""
