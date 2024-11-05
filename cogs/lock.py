# lock.py

import asyncio
from discord.ext import commands

class EventLockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dictionary to store event locks
        self.event_locks = {}

    async def is_event_handled(self, event_key: str) -> bool:
        """Check if an event has been handled."""
        return self.event_locks.get(event_key, False)

    async def set_event_handled(self, event_key: str):
        """Mark an event as handled."""
        self.event_locks[event_key] = True

    async def clear_event_lock(self, event_key: str, duration: int = 10):
        """Clear the lock after a certain duration."""
        await asyncio.sleep(duration)
        if event_key in self.event_locks:
            del self.event_locks[event_key]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Create a unique key for each reaction event
        event_key = f"{reaction.message.id}-{reaction.emoji}-{user.id}"

        # Check if this event has been handled by any instance
        if await self.is_event_handled(event_key):
            print(f"Event {event_key} already handled by another instance.")
            return

        # Mark this event as handled
        await self.set_event_handled(event_key)

        try:
            # Your reaction handling logic here
            print(f"Handling reaction event {event_key}")
            # Example: Processing the reaction event (adjust as needed)
            await reaction.message.channel.send(f"{user.mention} reacted with {reaction.emoji}")
        finally:
            # Clear the event lock after a set time to allow future handling if necessary
            await self.clear_event_lock(event_key, duration=10)

async def setup(bot):
    await bot.add_cog(EventLockCog(bot))
