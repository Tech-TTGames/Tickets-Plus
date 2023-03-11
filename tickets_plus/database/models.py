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

    # Simple columns
    guild_id: Mapped[int] = mapped_column(primary_key=True)
    open_message: Mapped[str] = mapped_column(
        default="Staff notes for Ticket $channel.", nullable=False
    )
    staff_team_name: Mapped[str] = mapped_column(default="Staff Team", nullable=False)

    # Relationships
    ticket_users: Mapped[List["TicketUser"]] = relationship(
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

    # Toggles
    msg_discovery: Mapped[bool] = mapped_column(default=True, nullable=False)
    strip_buttons: Mapped[bool] = mapped_column(default=False, nullable=False)


class TicketUser(Base):
    """Ticket users table"""

    __tablename__ = "ticket_users"

    # Simple columns
    user_id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="ticket_users", lazy="selectin"
    )


class StaffRole(Base):
    """Staff roles table"""

    __tablename__ = "staff_roles"

    # Simple columns
    role_id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="staff_roles", lazy="selectin")


class ObserversRole(Base):
    """Observer roles table"""

    __tablename__ = "observer_roles"

    # Simple columns
    role_id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="observers_roles", lazy="selectin"
    )


class CommunityRole(Base):
    """Community roles table"""

    __tablename__ = "community_roles"

    # Simple columns
    role_id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="community_roles", lazy="selectin"
    )


class CommunityPing(Base):
    """Community pings table"""

    __tablename__ = "community_pings"

    # Simple columns
    role_id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="community_pings", lazy="selectin"
    )


class Member(Base):
    """Members table"""

    __tablename__ = "members"

    # Simple columns
    id: Mapped[int] = mapped_column(primary_key=True, comment="User reference ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="community_roles", lazy="selectin"
    )
    user: Mapped["User"] = relationship(back_populates="members", lazy="selectin")


class User(Base):
    """Users table"""

    __tablename__ = "users"

    # Simple columns
    user_id: Mapped[int] = mapped_column(primary_key=True)

    # Relationships
    members: Mapped[List["Member"]] = relationship(back_populates="user", lazy="raise")

    # Toggles
    is_owner: Mapped[bool] = mapped_column(default=False)
