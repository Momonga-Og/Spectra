import asyncio
import redis
from discord.ext import commands

class EventLockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Connect to Redis (adjust host/port as needed)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    async def is_event_handled(self, event_key: str) -> bool:
        """Check if an event has been handled in Redis."""
        return self.redis_client.exists(event_key)

    async def set_event_handled(self, event_key: str, duration: int = 10):
        """Mark an event as handled in Redis with an expiration time."""
        self.redis_client.set(event_key, "handled", ex=duration)

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
        except Exception as e:
            print(f"Error handling event {event_key}: {e}")

async def setup(bot):
    await bot.add_cog(EventLockCog(bot))
