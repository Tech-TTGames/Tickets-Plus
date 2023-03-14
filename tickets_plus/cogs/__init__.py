"""A import utility for loading all cogs in this submodule.

This file just makes it easier to load all cogs in this submodule.
We can just import this submodule and iterate over the EXTENSIONS list.

Typical usage example:
    ```py
    from tickets_plus import cogs
    for extension in cogs.EXTENSIONS:
        await bot.load_extension(extension)
    ```
"""
# License: EPL-2.0
# Copyright (c) 2021-present The Tickets Plus Contributors
import pkgutil

EXTENSIONS = [
    module.name for module in pkgutil.iter_modules(__path__, f"{__package__}.")
]
"""A list of all cogs in this submodule. This is the list of cogs to load."""
