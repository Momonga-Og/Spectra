import asyncio
import aioredis
from discord.ext import commands

class EventLockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis_client = None  # Redis client initialized later

    async def connect_to_redis(self):
        """Initialize the Redis connection asynchronously."""
        self.redis_client = await aioredis.from_url("redis://localhost")

    async def is_event_handled(self, event_key: str) -> bool:
        """Check if an event has already been processed."""
        return await self.redis_client.exists(event_key) > 0

    async def set_event_handled(self, event_key: str, duration: int = 10):
        """Mark an event as handled in Redis with an expiration time."""
        await self.redis_client.set(event_key, "handled", ex=duration)

    async def handle_event(self, event_key: str, action):
        """Central handler to check lock status, set lock, and perform action."""
        if await self.is_event_handled(event_key):
            print(f"Event {event_key} already handled by another instance.")
            return False

        # Set the event as handled
        await self.set_event_handled(event_key)

        try:
            await action()  # Execute the provided action function
            print(f"Handled event {event_key}")
            return True
        except Exception as e:
            print(f"Error handling event {event_key}: {e}")
            return False

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        event_key = f"reaction-{reaction.message.id}-{reaction.emoji}-{user.id}"

        # Define the action to be executed if the lock allows it
        async def action():
            await reaction.message.channel.send(f"{user.mention} reacted with {reaction.emoji}")

        await self.handle_event(event_key, action)

    async def cog_load(self):
        """Connect to Redis when the cog is loaded."""
        await self.connect_to_redis()

    async def cog_unload(self):
        """Close the Redis connection when the cog is unloaded."""
        if self.redis_client:
            await self.redis_client.close()

async def setup(bot):
    cog = EventLockCog(bot)
    await cog.cog_load()  # Ensure Redis is connected on load
    await bot.add_cog(cog)
