"""A layer for the database session.

This module contains the `OnlineConfig` class.
It is used to make the database session easier to use.
It is also a async context manager.
Generally, you should use this class instead of the session directly.
Addionally, of note is the fact that one-on-one relationships are loaded
by default. But any relationship that is a one-to-many or many-to-many
relationship is not loaded by default.
This is due to efficiency concerns.
If you need to load a relationship, you can use the options argument, which
is a list of `sqlalchemy.sql.base.ExecutableOption`s.
For more information on `ExecutableOption`s, see the SQLAlchemy documentation.

Typical usage example:
    ```py
    async with OnlineConfig(bot, session) as db:
        guild = await db.get_guild(guild_id)
        # Do something with the guild
        # and if you changed something
        await db.commit()
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
from types import TracebackType
from typing import Sequence, Tuple, Type

from discord.ext import commands
from sqlalchemy import sql
from sqlalchemy.ext import asyncio as sa_asyncio
from sqlalchemy.sql import base
# Future Proofing for possible future use of asyncio

from tickets_plus.database import models


class OnlineConfig:
    """A convinience layer for the database session.

    This class is used to make the database session easier to use.
    It also handles the async with statement.
    Any and all commits have to be done manually.
    """

    def __init__(self, bot_instance: commands.AutoShardedBot,
                 session: sa_asyncio.AsyncSession) -> None:
        """Initialises the database session layer.

        Wraps the provided session in a async context manager.
        And sets the bot instance as a private attribute.

        Args:
            bot_instance: The bot instance.
            session: The database session.
        """
        self._session = session
        self._bot = bot_instance

    async def __aenter__(self) -> "OnlineConfig":
        """Enter the async with statement.

        This method is called when entering the async with statement.

        Returns:
            OnlineConfig: The database session layer.
        """
        return self

    async def __aexit__(self, exc_type: Type[BaseException] | None,
                        exc_value: BaseException | None,
                        traceback: TracebackType | None) -> None:
        """Exit the async with statement.

        This method is called when exiting the async with statement.
        Or when an exception is raised.
        We rollback the session if an exception is raised.
        We then close the session regardless.

        Args:
            exc_type: The exception type.
            exc_value: The exception value.
            traceback: The traceback.
        """
        if exc_type:
            await self.rollback()
        await self.close()

    async def close(self) -> None:
        """Close the database session.

        This method closes the underlying SQLAlchemy session.
        """
        await self._session.close()

    async def flush(self) -> None:
        """Flush the database session.

        Moves all the changes to the database transaction.
        """
        await self._session.flush()

    async def commit(self) -> None:
        """Commit the database session.

        Commits the underlying SQLAlchemy session.
        """
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the database session.

        Cleans all the non-committed changes.
        This includes the flushed changes.
        """
        await self._session.rollback()

    async def delete(self, obj) -> None:
        """Delete a row from the database.

        Marks the object for deletion.
        The deletion will be done on next flush.
        """
        await self._session.delete(obj)

    async def get_guild(
            self,
            guild_id: int,
            options: Sequence[base.ExecutableOption] | None = None
    ) -> models.Guild:
        """Get or create a guild from the database.

        Fetches a guild from the database.
        Due to the convienience of the database layer,
        we guarantee a guild will always be returned.
        It will be created if it does not exist.
        However, we do not commit the changes.

        Args:
            guild_id: The guild ID.
            options: The options to use when querying the database.
                Those options are mostly used for relationship loading.
                As in async we can't use lazy loading.

        Returns:
            models.Guild: The guild.
                With the relationships loaded if options are provided.
                Otherwise attempting to access the relationships will
                result in an error.
        """
        if options:
            guild_conf = await self._session.scalar(
                sql.select(models.Guild).where(
                    models.Guild.guild_id == guild_id).options(*options))
        else:
            guild_conf = await self._session.scalar(
                sql.select(
                    models.Guild).where(models.Guild.guild_id == guild_id))
        if guild_conf is None:
            guild_conf = models.Guild(guild_id=guild_id)
            self._session.add(guild_conf)
        return guild_conf

    async def get_user(
            self,
            user_id: int,
            options: Sequence[base.ExecutableOption] | None = None
    ) -> models.User:
        """Get or create a user from the database.

        Fetches a user from the database.
        Due to the convienience of the database layer,
        we guarantee a user will always be returned.
        It will be created if it does not exist.
        However, we do not commit the changes.

        Args:
            user_id: The user ID.
            options: The options to use when querying the database.
                Those options are mostly used for relationship loading.
                As in async we can't use lazy loading.

        Returns:
            models.User: The user.
                With the relationships loaded if options are provided.
                Otherwise attempting to access the relationships will
                result in an error.
        """
        if options:
            user = await self._session.scalar(
                sql.select(models.User).where(
                    models.User.user_id == user_id).options(*options))
        else:
            user = await self._session.scalar(
                sql.select(models.User).where(models.User.user_id == user_id))
        if user is None:
            user = models.User(user_id=user_id)
            self._session.add(user)
        return user

    async def get_member(self, user_id: int, guild_id: int) -> models.Member:
        """Get or create a member from the database.

        Fetches a member from the database.
        If the member does not exist, it will be created.
        We also check if the guild exists and create it if it does not.
        We also check if the user exists and create it if it does not.

        Args:
            user_id: The user ID.
            guild_id: The guild ID.

        Returns:
            models.Member: The member.
                As members have a one-to-one relationship with guilds,
                and a one-to-one relationship with users, we automatically
                load the guild and user relationships.
        """
        guild = await self.get_guild(guild_id)
        user = await self.get_user(user_id)
        member_conf = await self._session.scalar(
            sql.select(models.Member).where(models.Member.user == user,
                                            models.Member.guild == guild))
        if member_conf is None:
            member_conf = models.Member(user=user, guild=guild)
            self._session.add(member_conf)
        return member_conf

    async def get_ticket_bot(self, user_id: int,
                             guild_id: int) -> Tuple[bool, models.TicketBot]:
        """Get or create a ticket bot from the database.

        Fetches a ticket bot from the database.
        If the ticket bot does not exist, it will be created.
        We also check if the guild exists and create it if it does not.

        Args:
            user_id: The user ID.
            guild_id: The guild ID.

        Returns:
            Tuple[bool, models.TicketBot]: A tuple containing a boolean
                indicating if the ticket bot was created, and the ticket bot.
                Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        ticket_user = await self._session.scalar(
            sql.select(models.TicketBot).where(
                models.TicketBot.user_id == user_id,
                models.TicketBot.guild == guild))
        new = False
        if ticket_user is None:
            new = True
            ticket_user = models.TicketBot(user_id=user_id, guild=guild)
            self._session.add(ticket_user)
        return new, ticket_user

    async def check_ticket_bot(self, user_id: int, guild_id: int) -> bool:
        """Check if the ticket user exists.

        A more efficient way to check if a ticket user exists.
        Instead of attempting to create the ticket user,
        we just check if it exists.
        This is the only check that uses a guild ID.
        This is because the user ID is shared across all guilds.

        Args:
            user_id: The user ID.
            guild_id: The guild ID.

        Returns:
            bool: A boolean indicating if the ticket user exists.
        """
        ticket_user = await self._session.scalar(
            sql.select(models.TicketBot).where(
                models.TicketBot.user_id == user_id,
                models.TicketBot.guild_id == guild_id))
        return ticket_user is not None

    async def fetch_ticket(self, channel_id: int) -> models.Ticket | None:
        """Fetch a ticket from the database.

        Attempts to fetch a ticket from the database.
        If the ticket does not exist, None is returned.
        If you want to create a ticket if it does not exist,
        use get_ticket instead.

        Args:
            channel_id: The channel ID.

        Returns:
            models.Ticket | None: The ticket.
        """
        ticket = await self._session.get(models.Ticket, channel_id)
        return ticket

    async def get_ticket(
            self,
            channel_id: int,
            guild_id: int,
            staff_note: int | None = None) -> Tuple[bool, models.Ticket]:
        """Get a or create ticket from the database.

        Fetches a ticket from the database.
        If the ticket does not exist, it will be created.
        We also check if the guild exists and create it if it does not.
        If you want to check if a ticket exists, use fetch_ticket instead.

        Args:
            channel_id: The channel ID.
            guild_id: The guild ID. Used to create the guild if missing.
            staff_note: The staff note thread ID. Used to annotate the thread,
                if the ticket is created.

        Returns:
            Tuple[bool, models.Ticket]: A tuple containing a boolean
                indicating if the ticket was created, and the ticket.
                Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        ticket = await self._session.get(models.Ticket, channel_id)
        new = False
        if ticket is None:
            new = True
            ticket = models.Ticket(channel_id=channel_id,
                                   guild=guild,
                                   staff_note_thread=staff_note)
            self._session.add(ticket)
        return new, ticket

    async def get_staff_role(self, role_id: int,
                             guild_id: int) -> Tuple[bool, models.StaffRole]:
        """Get or create the staff role from the database.

        Fetches a staff role from the database.
        If the staff role does not exist, it will be created.
        We also check if the guild exists and create it if it does not.

        Args:
            role_id: The role ID.
            guild_id: The guild ID.

        Returns:
            Tuple[bool, models.StaffRole]: A tuple containing a boolean
                indicating if the staff role was created, and the staff role.
                Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        staff_role = await self._session.get(models.StaffRole, role_id)
        new = False
        if staff_role is None:
            new = True
            staff_role = models.StaffRole(role_id=role_id, guild=guild)
            self._session.add(staff_role)
        return new, staff_role

    async def get_all_staff_roles(self,
                                  guild_id: int) -> Sequence[models.StaffRole]:
        """Get all staff roles from the database.

        Fetches all staff roles from the database.
        If the staff roles do not exist, an empty list is returned.

        Args:
            guild_id: The guild ID.

        Returns:
            Sequence[models.StaffRole]: A list of staff roles.
                Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        staff_roles = await self._session.scalars(
            sql.select(models.StaffRole).where(models.StaffRole.guild == guild))
        return staff_roles.all()

    async def check_staff_role(self, role_id: int) -> bool:
        """Check if the staff role exists.

        A more efficient way to check if a staff role exists.
        Instead of attempting to create the staff role,
        we just check if it exists.

        Args:
            role_id: The role ID.

        Returns:
            bool: A boolean indicating if the staff role exists.
        """
        staff_role = await self._session.get(models.StaffRole, role_id)
        return staff_role is not None

    async def get_observers_role(
            self, role_id: int,
            guild_id: int) -> Tuple[bool, models.ObserversRole]:
        """Get or create the observers role from the database.

        Fetches a observers role from the database.
        If the observers role does not exist, it will be created.
        We also check if the guild exists and create it if it does not.

        Args:
            role_id: The role ID.
            guild_id: The guild ID.

        Returns:
            Tuple[bool, models.ObserversRole]: A tuple containing a boolean
                indicating if the observers role was created, and the observers
                role. Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        observers_role = await self._session.get(models.ObserversRole, role_id)
        new = False
        if observers_role is None:
            new = True
            observers_role = models.ObserversRole(role_id=role_id, guild=guild)
            self._session.add(observers_role)
        return new, observers_role

    async def get_all_observers_roles(
            self, guild_id: int) -> Sequence[models.ObserversRole]:
        """Get all observers roles from the database.

        Fetches all observers roles from the database.
        If the observers roles do not exist, an empty list is returned.

        Args:
            guild_id: The guild ID.

        Returns:
            Sequence[models.ObserversRole]: A list of observers roles.
                Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        observers_roles = await self._session.scalars(
            sql.select(
                models.ObserversRole).where(models.ObserversRole.guild == guild)
        )
        return observers_roles.all()

    async def check_observers_role(self, role_id: int) -> bool:
        """Check if the observers role exists.

        A more efficient way to check if a observers role exists.
        Instead of attempting to create the observers role,
        we just check if it exists.

        Args:
            role_id: The role ID.

        Returns:
            bool: A boolean indicating if the observers role exists.
        """
        observers_role = await self._session.get(models.ObserversRole, role_id)
        return observers_role is not None

    async def get_community_role(
            self, role_id: int,
            guild_id: int) -> Tuple[bool, models.CommunityRole]:
        """Get or create the community role from the database.

        Fetches a community role from the database.
        If the community role does not exist, it will be created.
        We also check if the guild exists and create it if it does not.

        Args:
            role_id: The role ID.
            guild_id: The guild ID.

        Returns:
            Tuple[bool, models.CommunityRole]: A tuple containing a boolean
                indicating if the community role was created, and the community
                role. Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        community_role = await self._session.get(models.CommunityRole, role_id)
        new = False
        if community_role is None:
            new = True
            community_role = models.CommunityRole(role_id=role_id, guild=guild)
            self._session.add(community_role)
        return new, community_role

    async def get_all_community_roles(
            self, guild_id: int) -> Sequence[models.CommunityRole]:
        """Get all community roles from the database.

        Fetches all community roles from the database.
        If the community roles do not exist, an empty list is returned.

        Args:
            guild_id: The guild ID.

        Returns:
            Sequence[models.CommunityRole]: A list of community roles.
                Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        community_roles = await self._session.scalars(
            sql.select(
                models.CommunityRole).where(models.CommunityRole.guild == guild)
        )
        return community_roles.all()

    async def check_community_role(self, role_id: int) -> bool:
        """Check if the community role exists.

        A more efficient way to check if a community role exists.
        Instead of attempting to create the community role,
        we just check if it exists.

        Args:
            role_id: The role ID.

        Returns:
            bool: A boolean indicating if the community role exists.
        """
        community_role = await self._session.get(models.CommunityRole, role_id)
        return community_role is not None

    async def get_community_ping(
            self, role_id: int,
            guild_id: int) -> Tuple[bool, models.CommunityPing]:
        """Get or create the community ping from the database.

        Fetches a community ping from the database.
        If the community ping does not exist, it will be created.
        We also check if the guild exists and create it if it does not.

        Args:
            role_id: The role ID.
            guild_id: The guild ID.

        Returns:
            Tuple[bool, models.CommunityPing]: A tuple containing a boolean
                indicating if the community ping was created, and the community
                ping. Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        community_ping = await self._session.get(models.CommunityPing, role_id)
        new = False
        if community_ping is None:
            new = True
            community_ping = models.CommunityPing(role_id=role_id, guild=guild)
            self._session.add(community_ping)
        return new, community_ping

    async def get_all_community_pings(
            self, guild_id: int) -> Sequence[models.CommunityPing]:
        """Get all community pings from the database.

        Fetches all community pings from the database.
        If the community pings do not exist, an empty list is returned.

        Args:
            guild_id: The guild ID.

        Returns:
            Sequence[models.CommunityPing]: A list of community pings.
                Relationships are loaded.
        """
        guild = await self.get_guild(guild_id)
        community_pings = await self._session.scalars(
            sql.select(
                models.CommunityPing).where(models.CommunityPing.guild == guild)
        )
        return community_pings.all()

    async def check_community_ping(self, role_id: int) -> bool:
        """Check if the community ping exists.

        A more efficient way to check if a community ping exists.
        Instead of attempting to create the community ping,
        we just check if it exists.

        Args:
            role_id: The role ID.

        Returns:
            bool: A boolean indicating if the community ping exists.
        """
        community_ping = await self._session.get(models.CommunityPing, role_id)
        return community_ping is not None
