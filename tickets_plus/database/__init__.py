"""General database package for Tickets+.

This package contains the database layer, models and statvars.
It is used by the bot to store and retrieve data from the database.
Or to get configuration values from the statvars module.

Typical usage example:
    ```py
    from tickets_plus.database import layer
    from tickets_plus.database import models
    from tickets_plus.database import statvars
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
from tickets_plus.database import layer
from tickets_plus.database import models
from tickets_plus.database import statvars
