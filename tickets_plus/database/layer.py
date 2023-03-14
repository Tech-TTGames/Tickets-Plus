"""A layer for the database session."""
from typing import Optional, Sequence, Tuple

from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.sql.base import ExecutableOption

from tickets_plus.database.models import (CommunityPing, CommunityRole, Guild,
                                          Member, ObserversRole, StaffRole,
                                          Ticket, TicketBot, User)


class OnlineConfig:
    """A convinience layer for the database session."""

    def __init__(self, bot: commands.AutoShardedBot,
                 session: AsyncSession) -> None:
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
            self,
            guild_id: int,
            options: Optional[Sequence[ExecutableOption]] = None) -> Guild:
        """Get or create a guild from the database."""
        if options:
            guild_conf = await self._session.scalar(
                select(Guild).where(Guild.guild_id == guild_id).options(
                    *options))
        guild_conf = await self._session.scalar(
            select(Guild).where(Guild.guild_id == guild_id))
        if guild_conf is None:
            guild_conf = Guild(guild_id=guild_id)
            self._session.add(guild_conf)
        return guild_conf

    async def get_user(
            self,
            user_id: int,
            options: Optional[Sequence[ExecutableOption]] = None) -> User:
        """Get or create a user from the database."""
        if options:
            user = await self._session.scalar(
                select(User).where(User.user_id == user_id).options(*options))
        user = await self._session.scalar(
            select(User).where(User.user_id == user_id))
        if user is None:
            user = User(user_id=user_id)
            self._session.add(user)
        return user

    async def get_member(self, user_id: int, guild_id: int) -> Member:
        """Get or create a member from the database."""
        guild = await self.get_guild(guild_id)
        user = await self.get_user(user_id)
        member_conf = await self._session.scalar(
            select(Member).where(Member.user == user, Member.guild == guild))
        if member_conf is None:
            member_conf = Member(user=user, guild=guild)
            self._session.add(member_conf)
        return member_conf

    async def get_ticket_bot(self, user_id: int,
                             guild_id: int) -> Tuple[bool, TicketBot]:
        """Get or create a ticket bot from the database."""
        guild = await self.get_guild(guild_id)
        ticket_user = await self._session.scalar(
            select(TicketBot).where(TicketBot.user_id == user_id,
                                    TicketBot.guild == guild))
        new = False
        if ticket_user is None:
            new = True
            ticket_user = TicketBot(user_id=user_id, guild=guild)
            self._session.add(ticket_user)
        return new, ticket_user

    async def check_ticket_bot(self, user_id: int, guild_id: int) -> bool:
        """Check if the ticket user exists."""
        ticket_user = await self._session.scalar(
            select(TicketBot).where(TicketBot.user_id == user_id,
                                    TicketBot.guild_id == guild_id))
        return ticket_user is not None

    async def fetch_ticket(self, channel_id: int) -> Optional[Ticket]:
        """Get a ticket from the database."""
        ticket = await self._session.get(Ticket, channel_id)
        return ticket

    async def get_ticket(self, channel_id: int, guild_id: int,
                         staff_note: Optional[int]) -> Tuple[bool, Ticket]:
        """Get a or create ticket from the database."""
        guild = await self.get_guild(guild_id)
        ticket = await self._session.get(Ticket, channel_id)
        new = False
        if ticket is None:
            new = True
            ticket = Ticket(channel_id=channel_id,
                            guild=guild,
                            staff_note_thread=staff_note)
            self._session.add(ticket)
        return new, ticket

    async def get_staff_role(self, role_id: int,
                             guild_id: int) -> Tuple[bool, StaffRole]:
        """Get or create the staff role from the database."""
        guild = await self.get_guild(guild_id)
        staff_role = await self._session.get(StaffRole, role_id)
        new = False
        if staff_role is None:
            new = True
            staff_role = StaffRole(role_id=role_id, guild=guild)
            self._session.add(staff_role)
        return new, staff_role

    async def get_all_staff_roles(self, guild_id: int) -> Sequence[StaffRole]:
        """Get all staff roles from the database."""
        guild = await self.get_guild(guild_id)
        staff_roles = await self._session.scalars(
            select(StaffRole).where(StaffRole.guild == guild))
        return staff_roles.all()

    async def check_staff_role(self, role_id: int) -> bool:
        """Check if the staff role exists."""
        staff_role = await self._session.get(StaffRole, role_id)
        return staff_role is not None

    async def get_observers_role(self, role_id: int,
                                 guild_id: int) -> Tuple[bool, ObserversRole]:
        """Get or create the observers role from the database."""
        guild = await self.get_guild(guild_id)
        observers_role = await self._session.get(ObserversRole, role_id)
        new = False
        if observers_role is None:
            new = True
            observers_role = ObserversRole(role_id=role_id, guild=guild)
            self._session.add(observers_role)
        return new, observers_role

    async def get_all_observers_roles(self,
                                      guild_id: int) -> Sequence[ObserversRole]:
        """Get all observers roles from the database."""
        guild = await self.get_guild(guild_id)
        observers_roles = await self._session.scalars(
            select(ObserversRole).where(ObserversRole.guild == guild))
        return observers_roles.all()

    async def check_observers_role(self, role_id: int) -> bool:
        """Check if the observers role exists."""
        observers_role = await self._session.get(ObserversRole, role_id)
        return observers_role is not None

    async def get_community_role(self, role_id: int,
                                 guild_id: int) -> Tuple[bool, CommunityRole]:
        """Get or create the community role from the database."""
        guild = await self.get_guild(guild_id)
        community_role = await self._session.get(CommunityRole, role_id)
        new = False
        if community_role is None:
            new = True
            community_role = CommunityRole(role_id=role_id, guild=guild)
            self._session.add(community_role)
        return new, community_role

    async def get_all_community_roles(self,
                                      guild_id: int) -> Sequence[CommunityRole]:
        """Get all community roles from the database."""
        guild = await self.get_guild(guild_id)
        community_roles = await self._session.scalars(
            select(CommunityRole).where(CommunityRole.guild == guild))
        return community_roles.all()

    async def check_community_role(self, role_id: int) -> bool:
        """Check if the community role exists."""
        community_role = await self._session.get(CommunityRole, role_id)
        return community_role is not None

    async def get_community_ping(self, role_id: int,
                                 guild_id: int) -> Tuple[bool, CommunityPing]:
        """Get the community ping from the database."""
        guild = await self.get_guild(guild_id)
        community_ping = await self._session.get(CommunityPing, role_id)
        new = False
        if community_ping is None:
            new = True
            community_ping = CommunityPing(role_id=role_id, guild=guild)
            self._session.add(community_ping)
        return new, community_ping

    async def get_all_community_pings(self,
                                      guild_id: int) -> Sequence[CommunityPing]:
        """Get all community pings from the database."""
        guild = await self.get_guild(guild_id)
        community_pings = await self._session.scalars(
            select(CommunityPing).where(CommunityPing.guild == guild))
        return community_pings.all()

    async def check_community_ping(self, role_id: int) -> bool:
        """Check if the community ping exists."""
        community_ping = await self._session.get(CommunityPing, role_id)
        return community_ping is not None
