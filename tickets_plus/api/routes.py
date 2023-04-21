"""Routes for the API.

A factory function for the API is provided, which takes a
:class:`tickets_plus.bot.TicketsPlusBot` object and returns a
:class:`tornado.web.Application` object.

Typical usage example:
    ```py
    from tickets_plus.api import routes
    from tickets_plus import bot

    bot_instance = bot.TicketsPlusBot(...)
    app = routes.make_app(bot_instance)
    app.listen(443, ssl_options=...)
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
from tornado import web

from tickets_plus import bot
from tickets_plus.api import handlers


def make_app(bot_instance: bot.TicketsPlusBot) -> web.Application:
    """Prepare the API.

    Maps the routes to the handlers. Provides the bot object to the handlers.

    Args:
        bot_instance: The bot object.
    """
    data = {"bot_instance": bot_instance}
    routes = [
        (r"/", handlers.TicketHandler, data),
        (r"/override", handlers.OverrideHandler, data),
    ]
    return web.Application(routes)
