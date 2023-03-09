"""A layer for the database session."""
from typing import Optional, Sequence, Tuple

from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.sql.base import ExecutableOption

from tickets_plus.database.models import (
    CommunityRole,
    Guild,
    Member,
    ObserversRole,
    StaffRole,
    TicketUser,
)


class OnlineConfig:
    """A convinience layer for the database session."""

    def __init__(self, bot: commands.AutoShardedBot, session: AsyncSession) -> None:
        self._session = session
        self._bot = bot

    async def __aenter__(self) -> "OnlineConfig":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type:
            await self.rollback()
            await self.close()

    async def close(self) -> None:
        """Close the database session."""
        await self._session.close()

    async def commit(self) -> None:
        """Commit the database session."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the database session."""
        await self._session.rollback()

    async def delete(self, obj) -> None:
        """Delete a row from the database."""
        await self._session.delete(obj)

    async def get_guild(
        self, guild_id: int, options: Optional[Sequence[ExecutableOption]] = None
    ) -> Guild:
        """Get or create a guild from the database."""
        if options:
            guild_conf = await self._session.scalar(
                select(Guild).where(Guild.guild_id == guild_id).options(*options)
            )
        guild_conf = await self._session.scalar(
            select(Guild).where(Guild.guild_id == guild_id)
        )
        if guild_conf is None:
            guild_conf = Guild(guild_id=guild_id)
            self._session.add(guild_conf)
        return guild_conf

    async def get_member(self, user_id: int, guild_id: int) -> Member:
        """Get or create a member from the database."""
        guild = self.get_guild(guild_id)
        member_conf = await self._session.scalar(
            select(Member).where(Member.user_id == user_id, Member.guild == guild)
        )
        if member_conf is None:
            member_conf = Member(user_id=user_id, guild=guild)
            self._session.add(member_conf)
        return member_conf

    async def get_ticket_user(
        self, user_id: int, guild_id: int
    ) -> Tuple[bool, TicketUser]:
        """Get or create a ticket user from the database."""
        guild = await self.get_guild(guild_id)
        ticket_user = await self._session.get(TicketUser, user_id)
        new = False
        if ticket_user is None:
            new = True
            ticket_user = TicketUser(user_id=user_id, guild=guild)
            self._session.add(ticket_user)
        return new, ticket_user

    async def check_ticket_user(self, user_id: int) -> bool:
        """Check if the ticket user exists."""
        ticket_user = await self._session.get(TicketUser, user_id)
        return ticket_user is not None

    async def get_staff_role(
        self, role_id: int, guild_id: int
    ) -> Tuple[bool, StaffRole]:
        """Get or create the staff role from the database."""
        guild = await self.get_guild(guild_id)
        staff_role = await self._session.get(StaffRole, role_id)
        new = False
        if staff_role is None:
            new = True
            staff_role = StaffRole(role_id=role_id, guild=guild)
            self._session.add(staff_role)
        return new, staff_role

    async def check_staff_role(self, role_id: int) -> bool:
        """Check if the staff role exists."""
        staff_role = await self._session.get(StaffRole, role_id)
        return staff_role is not None

    async def get_observers_role(
        self, role_id: int, guild_id: int
    ) -> Tuple[bool, ObserversRole]:
        """Get or create the observers role from the database."""
        guild = await self.get_guild(guild_id)
        observers_role = await self._session.get(ObserversRole, role_id)
        new = False
        if observers_role is None:
            new = True
            observers_role = ObserversRole(role_id=role_id, guild=guild)
            self._session.add(observers_role)
        return new, observers_role

    async def check_observers_role(self, role_id: int) -> bool:
        """Check if the observers role exists."""
        observers_role = await self._session.get(ObserversRole, role_id)
        return observers_role is not None

    async def get_community_role(
        self, role_id: int, guild_id: int
    ) -> Tuple[bool, CommunityRole]:
        """Get or create the community role from the database."""
        guild = await self.get_guild(guild_id)
        community_role = await self._session.get(CommunityRole, role_id)
        new = False
        if community_role is None:
            new = True
            community_role = CommunityRole(role_id=role_id, guild=guild)
            self._session.add(community_role)
        return new, community_role

    async def check_community_role(self, role_id: int) -> bool:
        """Check if the community role exists."""
        community_role = await self._session.get(CommunityRole, role_id)
        return community_role is not None
