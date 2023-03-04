"""A layer for the database session."""
from discord.ext import commands
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from ticket_plus.database.models import Guild, Member


class OnlineConfig:
    """A convinience layer for the database session."""

    def __init__(self, bot: commands.Bot, engine: Engine) -> None:
        self._session = Session(engine)
        self._bot = bot

    def close(self) -> None:
        """Close the database session."""
        self._session.close()

    def commit(self) -> None:
        """Commit the database session."""
        self._session.commit()

    def rollback(self) -> None:
        """Rollback the database session."""
        self._session.rollback()

    def get_guild(self, guild_id: int) -> Guild:
        """Get a guild from the database."""
        guild_conf = self._session.get(Guild, guild_id)
        if guild_conf is None:
            guild_conf = Guild(guid=guild_id)
            self._session.add(guild_conf)
        return guild_conf

    def get_member(self, user_id: int, guild_id: int) -> Member:
        """Get a member from the database."""
        guild = self.get_guild(guild_id)
        member_conf = self._session.scalars(
            select(Member).where(Member.user_id == user_id, Member.guild == guild)
        ).first()
        if member_conf is None:
            member_conf = Member(user_id=user_id, guild=guild)
            self._session.add(member_conf)
        return member_conf
