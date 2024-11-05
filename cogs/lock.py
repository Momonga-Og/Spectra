import asyncio
import aioredis
from discord.ext import commands

class EventLockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Connect to Redis (adjust host/port as needed)
        self.redis_client = None  # Initialized later in an async method

    async def connect_to_redis(self):
        """Initialize the connection to Redis asynchronously."""
        self.redis_client = await aioredis.from_url("redis://localhost")

    async def is_event_handled(self, event_key: str) -> bool:
        """Check if an event has been handled in Redis."""
        return await self.redis_client.exists(event_key) > 0

    async def set_event_handled(self, event_key: str, duration: int = 10):
        """Mark an event as handled in Redis with an expiration time."""
        await self.redis_client.set(event_key, "handled", ex=duration)

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

    async def cog_load(self):
        """Connect to Redis when the cog is loaded."""
        await self.connect_to_redis()

    async def cog_unload(self):
        """Close the Redis connection when the cog is unloaded."""
        if self.redis_client:
            await self.redis_client.close()

async def setup(bot):
    cog = EventLockCog(bot)
    await cog.cog_load()  # Ensure Redis is connected when loading
    await bot.add_cog(cog)
