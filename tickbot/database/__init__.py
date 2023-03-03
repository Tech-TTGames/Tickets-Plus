"""Initialize the database package."""
from sqlalchemy import URL, create_engine

from tickbot.database.models import Base
from tickbot.database.statvars import MiniConfig

cnfg = MiniConfig()

url = URL.create(
    drivername=cnfg.getitem("dbtype", "postgresql+psycopg2"),
    username=cnfg.getitem("dbuser", "postgres"),
    password=cnfg.getitem("dbpass", "postgres"),
    host=cnfg.getitem("dbhost", "localhost"),
    port=cnfg.getitem("dbport", 5432),
    database=cnfg.getitem("dbname", "tickbot"),
)

engine = create_engine(url, logging_name="sqlalchemy.engine")

Base.metadata.create_all(engine)
