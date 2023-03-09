"""File for database models"""
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    """Base of SQLAlchemy models"""


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
        back_populates="guild", lazy="raise", default=[]
    )
    staff_roles: Mapped[List["StaffRole"]] = relationship(
        back_populates="guild", lazy="raise", default=[]
    )
    observers_roles: Mapped[List["ObserversRole"]] = relationship(
        back_populates="guild", lazy="raise", default=[]
    )
    community_roles: Mapped[List["CommunityRole"]] = relationship(
        back_populates="guild", lazy="raise", default=[]
    )
    members: Mapped[List["Member"]] = relationship(
        back_populates="guild", lazy="raise", default=[]
    )

    # Toggles
    msg_discovery: Mapped[bool] = mapped_column(default=True, nullable=False)
    strip_buttons: Mapped[bool] = mapped_column(default=False, nullable=False)

    def get_id_list(self, obj: str, attr: str) -> List[int]:
        """Get a list of IDs from a relationship"""
        if obj == "members":
            raise ValueError("Do not use this method for big lists!")
        return [getattr(item, attr) for item in getattr(self, obj)]


class TicketUser(Base):
    """Ticket users table"""

    __tablename__ = "ticket_users"

    # Simple columns
    user_id: Mapped[int] = mapped_column(primary_key=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="ticket_users", lazy="selectin", default=[]
    )


class StaffRole(Base):
    """Staff roles table"""

    __tablename__ = "staff_roles"

    # Simple columns
    role_id: Mapped[int] = mapped_column(primary_key=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="staff_roles", lazy="selectin", default=[]
    )


class ObserversRole(Base):
    """Observer roles table"""

    __tablename__ = "observer_roles"

    # Simple columns
    role_id: Mapped[int] = mapped_column(primary_key=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="observers_roles", lazy="selectin", default=[]
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


class Member(Base):
    """User table"""

    __tablename__ = "members"

    # Simple columns
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    guild_id: Mapped[int] = mapped_column(ForeignKey("general_configs.guild_id"))

    # Relationships
    guild: Mapped["Guild"] = relationship(
        back_populates="community_roles", lazy="selectin"
    )

    # Toggles
    is_owner: Mapped[bool] = mapped_column(default=False)
