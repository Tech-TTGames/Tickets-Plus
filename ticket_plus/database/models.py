"""File for database models"""
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base of SQLAlchemy models"""


class Guild(Base):
    """General configuration table"""

    __tablename__ = "general_config"

    # Simple columns
    guid: Mapped[int] = mapped_column(primary_key=True)
    open_message: Mapped[str] = mapped_column(default="Staff notes for Ticket $channel.",
                                               nullable=False
                                               )
    staff_team: Mapped[str] = mapped_column(default="Staff Team", nullable=False)

    # Relationships
    ticket_users: Mapped[List["TicketUser"]] = relationship(back_populates="guild")
    staff_roles: Mapped[List["StaffRole"]] = relationship(back_populates="guild")
    observers: Mapped[List["ObserversRole"]] = relationship(back_populates="guild")
    community_roles: Mapped[List["CommunityRole"]] = relationship(back_populates="guild")
    users: Mapped[List["User"]] = relationship(back_populates="guild")

    # Toggles
    msg_discovery: Mapped[bool] = mapped_column(default=True, nullable=False)
    strip_buttons: Mapped[bool] = mapped_column(default=False, nullable=False)


class TicketUser(Base):
    """Ticket users table"""

    __tablename__ = "ticket_users"

    # Simple columns
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_config.guid"))

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="ticket_users")


class StaffRole(Base):
    """Staff roles table"""

    __tablename__ = "staff_roles"

    # Simple columns
    guid: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_config.guid"))

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="staff_roles")


class ObserversRole(Base):
    """Observer roles table"""

    __tablename__ = "observer_roles"

    # Simple columns
    guid: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_config.guid"))

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="observers")


class CommunityRole(Base):
    """Community roles table"""

    __tablename__ = "community_roles"

    # Simple columns
    guid: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_config.guid"))

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="community_roles")


class User(Base):
    """User table"""

    __tablename__ = "users"

    # Simple columns
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_config.guid"))

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="community_roles")

    # Toggles
    is_owner: Mapped[bool] = mapped_column(default=False)
