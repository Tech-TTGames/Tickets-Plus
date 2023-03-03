from discord.ext import commands
from sqlalchemy import Engine
from sqlalchemy.orm import Session


class OnlineConfig:
    """A convinience layer for the database session."""

    def __init__(self, bot: commands.Bot, engine: Engine) -> None:
        self._session = Session(engine)
        self._bot = bot
