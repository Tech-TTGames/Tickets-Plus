"""File for database models"""
from typing import List

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

metadata_obj = MetaData(schema="tickets_plus")


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    """Base of SQLAlchemy models"""

    metadata = metadata_obj


class Guild(Base):
    """General configuration table"""

    __tablename__ = "general_configs"
    __table_args__ = {
        "comment": "Table for general configurations, this is the parent table for all-guild specific tables."
    }

    # Simple columns
    guild_id: Mapped[int] = mapped_column(
        primary_key=True, comment="Unique discord-provided guild ID", default=None
    )
    open_message: Mapped[str] = mapped_column(
        default="Staff notes for Ticket $channel.",
        nullable=False,
        comment="Message to send when a staff thread is opened",
    )
    staff_team_name: Mapped[str] = mapped_column(
        default="Staff Team", nullable=False, comment="Name of the staff team"
    )

    # Toggles
    msg_discovery: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Whether to allow message discovery"
    )
    strip_buttons: Mapped[bool] = mapped_column(
        default=False, nullable=False, comment="Whether to strip buttons from messages"
    )

    # Relationships
    ticket_bots: Mapped[List["TicketBot"]] = relationship(
        back_populates="guild", lazy="raise"
    )
    staff_roles: Mapped[List["StaffRole"]] = relationship(
        back_populates="guild", lazy="raise"
    )
    observers_roles: Mapped[List["ObserversRole"]] = relationship(
        back_populates="guild", lazy="raise"
    )
    community_roles: Mapped[List["CommunityRole"]] = relationship(
        back_populates="guild", lazy="raise"
    )
    community_pings: Mapped[List["CommunityPing"]] = relationship(
        back_populates="guild", lazy="raise"
    )
    members: Mapped[List["Member"]] = relationship(back_populates="guild", lazy="raise")


class TicketBot(Base):
    """Ticketing bots table"""

    __tablename__ = "ticket_bots"
    __table_args__ = {
        "comment": "Users that open the ticket channels, mostly the Tickets bot, but can be other users due to whitelabel options."
    }

    # Simple columns
    id: Mapped[int] = mapped_column(
        primary_key=True, comment="Unique reference ID of the ticket user"
    )
    user_id: Mapped[int] = mapped_column(
        nullable=False,
        comment="Unique discord-provided user ID, however this is not the primary key as it is not unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="ticket_users", lazy="selectin"
    )


class StaffRole(Base):
    """Staff roles table"""

    __tablename__ = "staff_roles"
    __table_args__ = {
        "comment": "Roles that are allowed to view ticket notes, and have acess to staff commands."
    }

    # Simple columns
    role_id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Unique discord-provided role ID, this is the primary key as it is unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="staff_roles", lazy="selectin")


class ObserversRole(Base):
    """Observer roles table"""

    __tablename__ = "observer_roles"
    __table_args__ = {"comment": "Roles that are automatically added to tickets notes."}

    # Simple columns
    role_id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Unique discord-provided role ID, this is the primary key as it is unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="observers_roles", lazy="selectin"
    )


class CommunityRole(Base):
    """Community roles table"""

    __tablename__ = "community_roles"
    __table_args__ = {
        "comment": "Roles that are allowed to view tickets, but aren't staff."
    }

    # Simple columns
    role_id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Unique discord-provided role ID, this is the primary key as it is unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="community_roles", lazy="selectin"
    )


class CommunityPing(Base):
    """Community pings table"""

    __tablename__ = "community_pings"
    __table_args__ = {
        "comment": "Table for community pings, pinged when a ticket is opened but after adding the community roles."
    }

    # Simple columns
    role_id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Unique discord-provided role ID, this is the primary key as it is unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="community_pings", lazy="selectin"
    )


class Member(Base):
    """Members table"""

    __tablename__ = "members"
    __table_args__ = {
        "comment": "Table for members, this is a combination of a user and a guild, as a user can be in multiple guilds."
    }

    # Simple columns
    id: Mapped[int] = mapped_column(primary_key=True, comment="User reference ID")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
        comment="Unique discord-provided user ID, however this is not the primary key as it is not unique across guilds",
    )
    guild_id: Mapped[int] = mapped_column(
        ForeignKey("general_configs.guild_id"),
        nullable=False,
        comment="Unique Guild ID of parent guild",
    )

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="community_roles", lazy="selectin"
    )
    user: Mapped["User"] = relationship(back_populates="members", lazy="selectin")


class User(Base):
    """Users table"""

    __tablename__ = "users"
    __table_args__ = {
        "comment": "Table for users, this is not a guild-specific table, as a user can be in multiple guilds."
    }

    # Simple columns
    user_id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Unique discord-provided user ID, this is the primary key as it is unique across guilds",
    )

    # Toggles
    is_owner: Mapped[bool] = mapped_column(
        default=False, comment="Is the user the owner of the bot?"
    )

    # Relationships
    members: Mapped[List["Member"]] = relationship(back_populates="user", lazy="raise")
