"""File for database models"""
# License: EPL-2.0
# Copyright (c) 2021-present The Tickets Plus Contributors
from sqlalchemy import BigInteger, DateTime, ForeignKey, MetaData, String
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

metadata_obj = MetaData(schema="tickets_plus")


class UTCnow(expression.FunctionElement):
    """Function to get current UTC time"""

    type = DateTime()
    inherit_cache = True


@compiles(UTCnow, "postgresql")
# This is as according to the docs, but pylint doesn't like it
# pylint: disable=unused-argument, invalid-name
def pg_UTCnow(element, compiler, **kw):
    """
    Compile the utcnow function

    Args:
      element:
      compiler:
      **kw:

    Returns:

    """
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class Base(DeclarativeBase):
    """Base of SQLAlchemy models"""

    metadata = metadata_obj


class Guild(Base):
    """General configuration table"""

    __tablename__ = "general_configs"
    __table_args__ = {
        "comment": ("Table for general configurations,"
                    " this is the parent table for all-guild specific tables.")
    }

    # Simple columns
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        comment="Unique discord-provided guild ID")
    open_message: Mapped[str] = mapped_column(
        String(200),
        default="Staff notes for Ticket $channel.",
        nullable=False,
        comment="Message to send when a staff thread is opened",
    )
    staff_team_name: Mapped[str] = mapped_column(
        String(40),
        default="Staff Team",
        nullable=False,
        comment="Name of the staff team",
    )
    first_autoclose: Mapped[int|None] = mapped_column(
        nullable=True,
        comment=
        "Number of minutes since open with no response to autoclose the ticket",
    )

    # Toggles
    msg_discovery: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Whether to allow message discovery")
    strip_buttons: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Whether to strip buttons from messages")

    # Relationships
    ticket_bots: Mapped[list["TicketBot"]] = relationship(
        back_populates="guild", lazy="raise")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="guild",
                                                   lazy="raise")
    staff_roles: Mapped[list["StaffRole"]] = relationship(
        back_populates="guild", lazy="raise")
    observers_roles: Mapped[list["ObserversRole"]] = relationship(
        back_populates="guild", lazy="raise")
    community_roles: Mapped[list["CommunityRole"]] = relationship(
        back_populates="guild", lazy="raise")
    community_pings: Mapped[list["CommunityPing"]] = relationship(
        back_populates="guild", lazy="raise")
    members: Mapped[list["Member"]] = relationship(back_populates="guild",
                                                   lazy="raise")
    # Disabled for now gets sqlalchemy confused
    # users: Mapped[list["User"]] = relationship(
    #    secondary="members", back_populates="guilds", lazy="raise", viewonly=True
    # )


class TicketBot(Base):
    """Ticketing bots table"""

    __tablename__ = "ticket_bots"
    __table_args__ = {
        "comment":
            ("Users that open the ticket channels, mostly the Tickets bot,"
             " but can be other users due to whitelabel options.")
    }

    # Simple columns
    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=False,
        comment=(
            "Unique discord-provided user ID."
            " Used in conjunction with guild_id to make a unique primary key"),
        primary_key=True,
        unique=False,
    )
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment=(
            "Unique Guild ID of parent guild."
            " Used in conjunction with user_id to make a unique primary key"),
        primary_key=True,
        unique=False,
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="ticket_bots",
                                          lazy="selectin")


class Ticket(Base):
    """Ticket channels table"""

    __tablename__ = "tickets"
    __table_args__ = {"comment": "Channels that are tickets are stored here."}

    # Simple columns
    channel_id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        comment="Unique discord-provided channel ID")
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )
    date_created: Mapped[DateTime] = mapped_column(
        DateTime(),
        nullable=False,
        comment="Date the ticket was created",
        server_default=UTCnow(),
    )
    last_response: Mapped[DateTime] = mapped_column(
        DateTime(),
        nullable=False,
        comment="Date the ticket was last responded to",
        server_default=UTCnow(),
    )
    staff_note_thread: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=True,
        comment="Unique discord-provided channel ID of the staff note thread",
        unique=True,
    )
    anonymous: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Whether the ticket is in anonymous mode")

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="tickets",
                                          lazy="selectin")


class StaffRole(Base):
    """Staff roles table"""

    __tablename__ = "staff_roles"
    __table_args__ = {
        "comment":
            "Roles that are allowed to view ticket notes, and have acess to staff commands."
    }

    # Simple columns
    role_id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        comment=
        "Unique discord-provided role ID, this is the primary key as it is unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="staff_roles",
                                          lazy="selectin")


class ObserversRole(Base):
    """Observer roles table"""

    __tablename__ = "observer_roles"
    __table_args__ = {
        "comment": "Roles that are automatically added to tickets notes."
    }

    # Simple columns
    role_id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        comment=
        "Unique discord-provided role ID, this is the primary key as it is unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="observers_roles",
                                          lazy="selectin")


class CommunityRole(Base):
    """Community roles table"""

    __tablename__ = "community_roles"
    __table_args__ = {
        "comment": "Roles that are allowed to view tickets, but aren't staff."
    }

    # Simple columns
    role_id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        comment=
        "Unique discord-provided role ID, this is the primary key as it is unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="community_roles",
                                          lazy="selectin")


class CommunityPing(Base):
    """Community pings table"""

    __tablename__ = "community_pings"
    __table_args__ = {
        "comment":
            "Table for community pings, pinged when a ticket is opened but after adding the community roles."
    }

    # Simple columns
    role_id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        comment=
        "Unique discord-provided role ID, this is the primary key as it is unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="community_pings",
                                          lazy="selectin")


class Member(Base):
    """Members table"""

    __tablename__ = "members"
    __table_args__ = {
        "comment":
            "Table for members, this is a combination of a user and a guild, as a user can be in multiple guilds."
    }

    # Simple columns
    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("users.user_id"),
        nullable=False,
        comment=
        "Unique discord-provided user ID. Used in conjunction with guild_id to make a unique primary key",
        primary_key=True,
        unique=False,
    )
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment=
        "Unique Guild ID of parent guild. Used in conjunction with user_id to make a unique primary key",
        primary_key=True,
        unique=False,
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="members",
                                          lazy="selectin")
    user: Mapped["User"] = relationship(back_populates="memberships",
                                        lazy="selectin")


class User(Base):
    """Users table"""

    __tablename__ = "users"
    __table_args__ = {
        "comment":
            "Table for users, this is not a guild-specific table, as a user can be in multiple guilds."
    }

    # Simple columns
    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        comment=
        "Unique discord-provided user ID, this is the primary key as it is unique across guilds",
    )

    # Toggles
    is_owner: Mapped[bool] = mapped_column(
        default=False, comment="Is the user the owner of the bot?")

    # Relationships
    memberships: Mapped[list["Member"]] = relationship(back_populates="user",
                                                       lazy="raise")
    # Disabled for now gets sqlalchemy confused
    # guilds: Mapped[list["Guild"]] = relationship(
    #    secondary="members", back_populates="users", lazy="raise", viewonly=True
    # )
