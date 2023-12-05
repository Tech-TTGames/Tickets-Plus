"""Legacy Tickets+ features.

This cog contains features that were present in the original Tickets+ bot, but
have since been phased out. They are kept here for backwards and allowing for their
functionality to still be used, but they are not capable of being enabled.
Should the feature stop working, it will be removed from the bot entirely,
as the features are not being maintained.

Typical example usage:
    ```py
    from tickets_plus.exr import legacy
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contributor, GPL-3.0-or-later.
from __future__ import annotations

import logging
import string
import discord

from tickets_plus.database import models, layer


async def thread_create(channel: discord.TextChannel, guild: models.Guild, confg: layer.OnlineConfig) -> discord.Thread:
    nts_thrd: discord.Thread = await channel.create_thread(
        name="Staff Notes",
        reason=f"Staff notes for Ticket {channel.name}",
        auto_archive_duration=10080,
    )
    await nts_thrd.send(string.Template(guild.open_message).safe_substitute(channel=channel.mention))
    logging.info("Created thread %s for %s", nts_thrd.name, channel.name)
    if guild.observers_roles:
        observer_ids = await confg.get_all_observers_roles(guild.guild_id)
        inv = await nts_thrd.send(" ".join([f"<@&{role.role_id}>" for role in observer_ids]))
        await inv.delete()
    return nts_thrd
