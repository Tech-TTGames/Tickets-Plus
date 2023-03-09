"""Initiates the bot"""
import asyncio

from tickets_plus import start_bot

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
