from discord.ext import commands
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from ticket_plus.database.models import User, Guild

class OnlineConfig:
    """A convinience layer for the database session."""

    def __init__(self, bot: commands.Bot, engine: Engine) -> None:
        self._session = Session(engine)
        self._bot = bot
    
    def get_guild(self, guild_id: int):
        """Get a guild from the database."""
        guild_conf = self._session.get(User, guild_id)
        if guild_conf is None:
            guild_conf = Guild(guid=guild_id)
            self._session.add(guild_conf)
            self._session.commit()
