"""File for database models.

This file contains the SQLAlchemy models for the database.
These models are used to create the database tables and
to interact with the database.
For more information on SQLAlchemy, please see the docs:
https://docs.sqlalchemy.org/en/20/

Typical usage example:
    ```py
    from tickets_plus.database import models
    models.Base.metadata.create_all(...)
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.

import datetime
from typing import Type

import sqlalchemy
from sqlalchemy import orm, sql
from sqlalchemy.ext import compiler as cmplr

_METADATA_OBJ = sqlalchemy.MetaData(schema="tickets_plus")
"""The metadata object for the database. Defines the schema."""


class UTCnow(sql.expression.FunctionElement):
    """Function to get current UTC time

    This is used to get the current UTC time database-side.
    Once again, read the SQLAlchemy docs for more information.

    Attributes:
        type: The type of the expression, in this case, a datetime object
        inherit_cache: Whether to inherit the cache, in this case, yes
    """

    type = sqlalchemy.DateTime()
    inherit_cache = True


@cmplr.compiles(UTCnow, "postgresql")
# This is as according to the docs, but pylint doesn't like it
# Can't implement this for sqlite because it doesn't time objects
# pylint: disable=unused-argument, invalid-name
def pg_UTCnow(element, compiler, **kw):
    """Compile the utcnow function for postgresql

    Please see the SQLAlchemy docs for more information.
    This script is based on the example given in the docs.

    Args:
      element: The element to compile so, in this case, the UTCnow object.
      compiler: The Compiled object, can be accessed to get information.
      **kw: Keyword arguments.

    Returns:
        The compiled SQL expression.
    """
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class Base(orm.DeclarativeBase):
    """Base of SQLAlchemy models

    This is the base class for all SQLAlchemy models.
    It is used to define the metadata object for the database.
    A detailed database schema is available in our docs.
    It includes a diagram of the database tables.
    Please see the SQLAlchemy docs for more information, about
    how to use this class.

    Attributes:
        metadata: The metadata object for the database.
    """

    metadata = _METADATA_OBJ


class Guild(Base):
    """General Guild-specific configuration table

    This is the general configuration table.
    It contains the general configuration for the bot.
    This includes the staff team name, the open message,
    and the autoclose time.
    It also contains the relationships to all other guild-specific tables.

    Attributes:
        guild_id: The unique discord-provided guild ID.
        open_message: The message to send when a staff thread is opened
            defaults to "Staff notes for Ticket $channel." and is
            limited to 200 characters.
        staff_team_name: The name of the staff team
            defaults to "Staff Team" and is limited to 40 characters.
        first_autoclose: Time since open with no response to autoclose.
        any_autoclose: Time since last response to autoclose.
        warn_autoclose: Time to warn user (via DM) after last response.
        msg_discovery: Whether to allow message discovery
            defaults to True.
        strip_buttons: Whether to strip buttons from messages
            defaults to False.
        ticket_bots: The relationship to the TicketBot table.
        tickets: The relationship to the Ticket table.
        staff_roles: The relationship to the StaffRole table.
        observers_roles: The relationship to the ObserversRole table.
        community_roles: The relationship to the CommunityRole table.
        community_pings: The relationship to the CommunityPing table.
        members: The relationship to the Member table.
    """

    __tablename__ = "general_configs"
    __table_args__ = {
        "comment": ("Table for general configurations,"
                    " this is the parent table for all-guild specific tables.")
    }

    # Simple columns
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        primary_key=True,
        comment="Unique discord-provided guild ID")
    open_message: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(200),
        default="Staff notes for Ticket $channel.",
        nullable=False,
        comment="Message to send when a staff thread is opened",
    )
    staff_team_name: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(40),
        default="Staff Team",
        nullable=False,
        comment="Name of the staff team",
    )
    first_autoclose: orm.Mapped[datetime.timedelta | None] = orm.mapped_column(
        sqlalchemy.Interval(),
        nullable=True,
        comment="Time since open with no response to autoclose")
    any_autoclose: orm.Mapped[datetime.timedelta | None] = orm.mapped_column(
        sqlalchemy.Interval(),
        nullable=True,
        comment="Time since last response to autoclose")
    warn_autoclose: orm.Mapped[datetime.timedelta | None] = orm.mapped_column(
        sqlalchemy.Interval(),
        nullable=True,
        comment="Time to warn user (via DM) after last response")
    support_block: orm.Mapped[int | None] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        nullable=True,
        comment=("Role to apply to users who are blocked from creating tickets"
                 " Please manually add this role to blacklist users on"
                 " https://ticketsbot.net/"
                 " If not set, considered disabled."))
    helping_block: orm.Mapped[int | None] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        nullable=True,
        comment=(
            "Role to apply to users who are blocked from helping in tickets"
            " I would reccomend also preventing the users from obtaining"
            " any other support roles."
            " Using permissions checks in reaction bots."
            " If not set, considered disabled."))

    # Toggles
    msg_discovery: orm.Mapped[bool] = orm.mapped_column(
        default=True,
        nullable=False,
        comment="Whether to allow message discovery")
    strip_buttons: orm.Mapped[bool] = orm.mapped_column(
        default=False,
        nullable=False,
        comment="Whether to strip buttons from messages")
    strip_roles: orm.Mapped[bool] = orm.mapped_column(
        default=False,
        nullable=False,
        comment="Whether to strip comsup roles when applying a helping_block")
    integrated: orm.Mapped[bool] = orm.mapped_column(
        default=False,
        nullable=False,
        comment="Whether the bot is integrated with the main bot")

    # Relationships
    ticket_bots: orm.Mapped[list["TicketBot"]] = orm.relationship(
        back_populates="guild", lazy="raise")
    tickets: orm.Mapped[list["Ticket"]] = orm.relationship(
        back_populates="guild", lazy="raise")
    staff_roles: orm.Mapped[list["StaffRole"]] = orm.relationship(
        back_populates="guild", lazy="raise")
    observers_roles: orm.Mapped[list["ObserversRole"]] = orm.relationship(
        back_populates="guild", lazy="raise")
    community_roles: orm.Mapped[list["CommunityRole"]] = orm.relationship(
        back_populates="guild", lazy="raise")
    community_pings: orm.Mapped[list["CommunityPing"]] = orm.relationship(
        back_populates="guild", lazy="raise")
    members: orm.Mapped[list["Member"]] = orm.relationship(
        back_populates="guild", lazy="raise")
    tags: orm.Mapped[list["Tag"]] = orm.relationship(back_populates="guild",
                                                     lazy="raise")
    ticket_types: orm.Mapped[list["TicketType"]] = orm.relationship(
        back_populates="guild", lazy="raise")
    # Disabled for now gets sqlalchemy confused
    # pylint: disable=line-too-long
    # users: orm.Mapped[list["User"]] = orm.relationship(
    #    secondary="members", back_populates="guilds", lazy="raise", viewonly=True
    # )

    # SNOWFLAKE PROTOCOL
    @orm.reconstructor
    def init_on_load(self):
        """Initiate snowflake protocol

        This is a snowflake protocol, which is a way to make the guild ID
        more accessible. To use with discord.py.
        """
        self.id = self.guild_id


class TicketBot(Base):
    """Guild-specific Ticket Bot table

    This is the table for the ticket bots.
    It contains the user ID of the ticket bot.
    It also contains the relationship to the Guild table.
    And the foreign key to the guild ID.

    Attributes:
        user_id: The unique discord-provided user ID
        guild_id: The unique discord-provided guild ID
        guild: The relationship to the Guild table
    """

    __tablename__ = "ticket_bots"
    __table_args__ = {
        "comment":
            ("Users that open the ticket channels, mostly the Tickets bot,"
             " but can be other users due to whitelabel options.")
    }

    # Simple columns
    user_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        nullable=False,
        comment=(
            "Unique discord-provided user ID."
            " Used in conjunction with guild_id to make a unique primary key"),
        primary_key=True,
        unique=False,
    )
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment=(
            "Unique Guild ID of parent guild."
            " Used in conjunction with user_id to make a unique primary key"),
        primary_key=True,
        unique=False,
    )

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(back_populates="ticket_bots",
                                                  lazy="selectin")


class TicketType(Base):
    """Categorize tickets based on the prefix of the channel name

    This is the table for the ticket types.
    It contains the prefix of the ticket type.
    It also contains the relationship to the Guild table.
    And the foreign key to the guild ID.
    And type-specific setting overrides.

    Attributes:
        prefix: The prefix of the ticket type. Also the, type name.
        guild_id: The unique discord-provided guild ID
        guild: The relationship to the Guild table
        comping: Whether to ping the community roles when template matches
        comaccs: Whether to ping the community roles when template matches
        strpbuttns: Whether to strip buttons from open when template matches
    """

    __tablename__ = "ticket_types"
    __table_args__ = {
        "comment": "Ticket types are stored here. Each guild can have multiple."
    }

    # Simple columns
    prefix: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(20),
        nullable=False,
        comment="The prefix of the ticket type",
        primary_key=True,
    )
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="The unique discord-provided guild ID",
        primary_key=True,
    )
    comping: orm.Mapped[bool] = orm.mapped_column(
        default=True,
        nullable=False,
        comment="Whether to ping the community roles when template matches")
    comaccs: orm.Mapped[bool] = orm.mapped_column(
        default=True,
        nullable=False,
        comment="Whether to add the community roles when template matches")
    strpbuttns: orm.Mapped[bool] = orm.mapped_column(
        default=True,
        nullable=False,
        comment="Whether to strip buttons from open when template matches")
    ignore: orm.Mapped[bool] = orm.mapped_column(
        default=False,
        nullable=False,
        comment="Whether to ignore this ticket type")

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(back_populates="ticket_types",
                                                  lazy="selectin")

    @classmethod
    def default(cls: Type["TicketType"]) -> "TicketType":
        """Default ticket type

        This is the default ticket type.
        It is used when no ticket type is specified.
        """
        return cls(prefix="",
                   guild_id=0,
                   comping=True,
                   comaccs=True,
                   strpbuttns=True,
                   ignore=False)


class Ticket(Base):
    """Ticket channels table

    This is the table for the ticket channels.
    It contains the channel ID of the ticket channel.
    It also contains the relationship to the Guild table.
    And the foreign key to the guild ID.
    Any closed tickets are deleted from this table.

    Attributes:
        channel_id: The unique discord-provided channel ID.
        guild_id: The unique discord-provided guild ID.
        user_id: The unique discord-provided user ID.
        date_created: The date the ticket was created.
        last_response: The date of the last response in the ticket.
        staff_note_thread: The unique discord-provided ID of the note thread.
        anonymous: Whether the ticket is in anonymous mode.
        guild: The relationship to the Guild table.
    """

    __tablename__ = "tickets"
    __table_args__ = {"comment": "Channels that are tickets are stored here."}

    # Simple columns
    channel_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        primary_key=True,
        comment="Unique discord-provided channel ID")
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )
    user_id: orm.Mapped[int | None] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        nullable=True,
        comment="Unique discord-provided user ID",
    )
    date_created: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime(),
        nullable=False,
        comment="Date the ticket was created",
        server_default=UTCnow(),
    )
    last_response: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime(),
        nullable=False,
        comment="Date the ticket was last responded to",
        server_default=UTCnow(),
    )
    staff_note_thread: orm.Mapped[int | None] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        nullable=True,
        comment="Unique discord-provided channel ID of the staff note thread",
        unique=True,
    )
    anonymous: orm.Mapped[bool] = orm.mapped_column(
        default=False,
        nullable=False,
        comment="Whether the ticket is in anonymous mode")
    notified: orm.Mapped[bool] = orm.mapped_column(
        default=False,
        nullable=False,
        comment="Whether the user has been notified about this ticket")

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(back_populates="tickets",
                                                  lazy="selectin")

    # SNOWFLAKE PROTOCOL
    @orm.reconstructor
    def init_on_load(self):
        """Initiate snowflake protocol

        This is a snowflake protocol, which is a way to make the channel ID
        more accessible. To use with discord.py.
        """
        self.id = self.channel_id


class Tag(Base):
    """Tags table.

    Stores the tags for the guild.
    Tags are used to quickly respond to common questions.
    Tags are stored in the database so they can be
    updated without restarting the bot.
    Additionally, if additional columns besides "tag" and "content" are added,
    the tag is automatically interpreted as a embed.

    Attributes:
        guild_id: The unique discord-provided guild ID.
        tag: The 'key' of the tag.
        title: The title of the embed.
        description: The description of the embed.
        url: The url of the embed.
        color: The color of the embed.
        footer: The footer of the embed.
        image: The image of the embed.
        thumbnail: The thumbnail of the embed.
        author: The author of the embed.
        guild: The relationship to the Guild table.
    """

    __tablename__ = "tags"
    __table_args__ = {"comment": "Tags for the guilds."}

    # Simple columns
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
        primary_key=True)
    tag_name: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(32),
        nullable=False,
        comment="The 'key' of the tag",
        primary_key=True)
    title: orm.Mapped[str | None] = orm.mapped_column(
        sqlalchemy.String(256), nullable=True, comment="The title of the embed")
    description: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(4096),
        nullable=False,
        comment="The description of the embed")
    url: orm.Mapped[str | None] = orm.mapped_column(
        sqlalchemy.String(256), nullable=True, comment="The url of the embed")
    color: orm.Mapped[int | None] = orm.mapped_column(
        sqlalchemy.Integer(), nullable=True, comment="The color of the embed")
    footer: orm.Mapped[str | None] = orm.mapped_column(
        sqlalchemy.String(2048),
        nullable=True,
        comment="The footer of the embed")
    image: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(256),
                                               nullable=True,
                                               comment="The image of the embed")
    thumbnail: orm.Mapped[str | None] = orm.mapped_column(
        sqlalchemy.String(256),
        nullable=True,
        comment="The thumbnail of the embed")
    author: orm.Mapped[str | None] = orm.mapped_column(
        sqlalchemy.String(256),
        nullable=True,
        comment="The author of the embed")

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(
        back_populates="tags",
        lazy="selectin",
    )


class StaffRole(Base):
    """Staff roles table

    This is the table for the staff roles.
    It contains the role ID of the staff role.
    It also contains the relationship to the Guild table.
    And the foreign key to the guild ID.

    Attributes:
        role_id: The unique discord-provided role ID.
        guild_id: The unique discord-provided guild ID.
        guild: The relationship to the Guild table.
    """

    __tablename__ = "staff_roles"
    __table_args__ = {
        "comment": ("Roles that are allowed to view ticket notes,"
                    " and have acess to staff commands.")
    }

    # Simple columns
    role_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        primary_key=True,
        comment=("Unique discord-provided role ID,"
                 " this is the primary key as it is unique across guilds"),
    )
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(back_populates="staff_roles",
                                                  lazy="selectin")

    # SNOWFLAKE PROTOCOL
    @orm.reconstructor
    def init_on_load(self):
        """Initiate snowflake protocol

        This is a snowflake protocol, which is a way to make the role ID
        more accessible. To use with discord.py.
        """
        self.id = self.role_id


class ObserversRole(Base):
    """Observer roles table

    This is the table for the observer roles.
    It contains the role ID of the observer role.
    It also contains the relationship to the Guild table.
    And the foreign key to the guild ID.

    Attributes:
        role_id: The unique discord-provided role ID.
        guild_id: The unique discord-provided guild ID.
        guild: The relationship to the Guild table.
    """

    __tablename__ = "observer_roles"
    __table_args__ = {
        "comment": "Roles that are automatically added to tickets notes."
    }

    # Simple columns
    role_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        primary_key=True,
        comment=("Unique discord-provided role ID,"
                 " this is the primary key as it is unique across guilds"),
    )
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(
        back_populates="observers_roles", lazy="selectin")

    # SNOWFLAKE PROTOCOL
    @orm.reconstructor
    def init_on_load(self):
        """Initiate snowflake protocol

        This is a snowflake protocol, which is a way to make the role ID
        more accessible. To use with discord.py.
        """
        self.id = self.role_id


class CommunityRole(Base):
    """Community roles table

    This is the table for the community roles.
    It contains the role ID of the community role.
    It also contains the relationship to the Guild table.
    And the foreign key to the guild ID.

    Attributes:
        role_id: The unique discord-provided role ID.
        guild_id: The unique discord-provided guild ID.
        guild: The relationship to the Guild table.
    """

    __tablename__ = "community_roles"
    __table_args__ = {
        "comment": "Roles that are allowed to view tickets, but aren't staff."
    }

    # Simple columns
    role_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        primary_key=True,
        comment=("Unique discord-provided role ID,"
                 " this is the primary key as it is unique across guilds"),
    )
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(
        back_populates="community_roles", lazy="selectin")

    # SNOWFLAKE PROTOCOL
    @orm.reconstructor
    def init_on_load(self):
        """Initiate snowflake protocol

        This is a snowflake protocol, which is a way to make the role ID
        more accessible. To use with discord.py.
        """
        self.id = self.role_id


class CommunityPing(Base):
    """Community pings table

    This is the table for the community pings.
    It contains the role ID of the community ping role.
    It also contains the relationship to the Guild table.
    And the foreign key to the guild ID.

    Attributes:
        role_id: The unique discord-provided role ID.
        guild_id: The unique discord-provided guild ID.
        guild: The relationship to the Guild table.
    """

    __tablename__ = "community_pings"
    __table_args__ = {
        "comment": ("Table for community pings,"
                    " pinged when a ticket is opened but"
                    " after adding the community roles.")
    }

    # Simple columns
    role_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        primary_key=True,
        comment=("Unique discord-provided role ID,"
                 " this is the primary key as it is unique across guilds"),
    )
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(
        back_populates="community_pings", lazy="selectin")

    # SNOWFLAKE PROTOCOL
    @orm.reconstructor
    def init_on_load(self):
        """Initiate snowflake protocol

        This is a snowflake protocol, which is a way to make the role ID
        more accessible. To use with discord.py.
        """
        self.id = self.role_id


class Member(Base):
    """Members table

    This is the table for the members.
    It is an association table between the users and the guilds.
    It contains the user ID and the guild ID.
    It also contains a relationship to both the User and Guild tables.
    It will also contain any bot information about the user.

    Attributes:
        user_id: The unique discord-provided user ID.
        guild_id: The unique discord-provided guild ID.
        user: The relationship to the User table.
        guild: The relationship to the Guild table.
    """

    __tablename__ = "members"
    __table_args__ = {
        "comment": ("Table for members,"
                    " this is a combination of a user and a guild,"
                    " as a user can be in multiple guilds.")
    }

    # Simple columns
    user_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("users.user_id"),
        nullable=False,
        comment=(
            "Unique discord-provided user ID."
            " Used in conjunction with guild_id to make a unique primary key"),
        primary_key=True,
        unique=False,
    )
    guild_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        sqlalchemy.ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment=(
            "Unique Guild ID of parent guild."
            " Used in conjunction with user_id to make a unique primary key"),
        primary_key=True,
        unique=False,
    )
    status: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.Integer(),
        nullable=False,
        default=0,
        comment=("The status of the member, 0 is normal, "
                 "1 is support-blocked, 2 is barred from providing support"),
    )
    status_till: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sqlalchemy.DateTime(),
        nullable=True,
        comment=("The time until the status is removed, "
                 "if None, the status is permanent"),
        default=None)

    # Relationships
    guild: orm.Mapped["Guild"] = orm.relationship(back_populates="members",
                                                  lazy="selectin")
    user: orm.Mapped["User"] = orm.relationship(back_populates="memberships",
                                                lazy="selectin")


class User(Base):
    """Users table

    This is the table for the users.
    It contains the user ID.
    It also contains a relationship to the Member table.
    It will also contain any bot information about the user.

    Attributes:
        user_id: The unique discord-provided user ID.
        memberships: The relationship to the Member table.
        is_owner: Is the user the owner of the bot?
    """

    __tablename__ = "users"
    __table_args__ = {
        "comment": ("Table for users,"
                    " this is not a guild-specific table,"
                    " as a user can be in multiple guilds.")
    }

    # Simple columns
    user_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger(),
        primary_key=True,
        comment=("Unique discord-provided user ID,"
                 " this is the primary key as it is unique across guilds"),
    )

    # Toggles
    is_owner: orm.Mapped[bool] = orm.mapped_column(
        default=False, comment="Is the user the owner of the bot?")

    # Relationships
    memberships: orm.Mapped[list["Member"]] = orm.relationship(
        back_populates="user", lazy="raise")
    # Disabled for now gets sqlalchemy confused
    # pylint: disable=line-too-long
    # guilds: orm.Mapped[list["Guild"]] = orm.relationship(
    #    secondary="members", back_populates="users", lazy="raise", viewonly=True
    # )

    # SNOWFLAKE PROTOCOL
    @orm.reconstructor
    def init_on_load(self):
        """Initiate snowflake protocol

        This is a snowflake protocol, which is a way to make the user ID
        more accessible. To use with discord.py.
        """
        self.id = self.user_id
