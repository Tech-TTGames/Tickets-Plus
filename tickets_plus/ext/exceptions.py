"""General exceptions that we can use in the application.

This module contains general exceptions that we can use in the application.
These exceptions are used to handle errors in a more elegant way. Most of these
exceptions are a subclass of `discord.app_commands.AppCommandError`.

Typical usage example:
    ```py
    from tickets_plus.ext import exceptions
    try:
        ...
    except exceptions.ReferenceNotFound:
        ...
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
from discord import app_commands


class TicketsPlusCommandError(app_commands.AppCommandError):
    """Base class for Tickets+ exceptions.

    This is the base class for all Tickets+ exceptions.
    Avoid using this exception, use a subclass of this exception instead.
    If you are using this exception, please consider creating a subclass of
    for your use case.
    This is a subclass of `discord.app_commands.AppCommandError` to use
    the library's app command handling functions.
    """


class TicketsCheckFailure(app_commands.CheckFailure):
    """Command failed ticket checks.

    An app command failed the ticket checks.
    This is usually used when a user tries to execute a command
    that is not allowed in the current ticket state.
    """


class ReferenceNotFound(TicketsPlusCommandError):
    """Command executed with invalid reference.

    A previously valid reference no longer resolves successfully.
    Mostly cause by manual deletion of the referenced object,
    by the user.
    """


class UsageError(TicketsPlusCommandError):
    """Command executed with invalid usage.

    An app command was executed with invalid usage.
    A broad Tickets+ exception that is used when a command is executed
    in an invalid way.
    """


class InvalidLocation(UsageError):
    """Command executed in an invalid location.

    An app command was executed in an invalid location.
    This is usually used when a command is executed in a DM channel,
    or in general, a channel that is invalid for the command.
    """


class InvalidParameters(UsageError):
    """Command executed with invalid parameters.

    An app command was executed with invalid parameters.
    This is usually used when a user provides invalid parameters to a command.
    """
