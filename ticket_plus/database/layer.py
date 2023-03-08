"""A layer for the database session."""
from typing import Optional, Sequence, Tuple

from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sqlalchemy.sql.base import ExecutableOption

from ticket_plus.database.models import Guild, Member, TicketUser


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
        """Get a guild from the database."""
        if options:
            guild_conf = await self._session.scalar(
                select(Guild).where(Guild.guid == guild_id).options(*options)
            )
        guild_conf = await self._session.scalar(
            select(Guild).where(Guild.guid == guild_id)
        )
        if guild_conf is None:
            guild_conf = Guild(guid=guild_id)
            self._session.add(guild_conf)
        return guild_conf

    async def get_member(self, user_id: int, guild_id: int) -> Member:
        """Get a member from the database."""
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
        """Get a ticket user from the database."""
        guild = await self.get_guild(guild_id)
        ticket_user = await self._session.scalar(
            select(TicketUser).where(
                TicketUser.user_id == user_id, TicketUser.guild == guild
            )
        )
        new = False
        if ticket_user is None:
            new = True
            ticket_user = TicketUser(user_id=user_id, guild=guild)
            self._session.add(ticket_user)
        return (new, ticket_user)
