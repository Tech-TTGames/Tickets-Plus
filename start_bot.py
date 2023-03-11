"""Initiates the bot"""
import asyncio
import sys

from tickets_plus import start_bot

if __name__ == "__main__":
    if (
        sys.platform == "win32"
    ):  # Psycopg3 doesn't work on Windows in async mode without this
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
