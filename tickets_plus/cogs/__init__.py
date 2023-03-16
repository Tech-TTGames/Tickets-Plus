"""A import utility for loading all cogs in this submodule.

This file just makes it easier to load all cogs in this submodule.
We can just import this submodule and iterate over the `EXTENSIONS` list.

Typical usage example:
    ```py
    from tickets_plus import bot
    from tickets_plus import cogs
    bot_instance = bot.TicketsPlusBot(...)
    for extension in cogs.EXTENSIONS:
        await bot_instance.load_extension(extension)
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets Plus Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import pkgutil

EXTENSIONS = [
    module.name for module in pkgutil.iter_modules(__path__, f"{__package__}.")
]
"""A list of all cogs in this submodule. This is the list of cogs to load."""
