import discord
from discord.ext import commands
import os
import asyncio
from utils.scheduler import schedule_reboot

# Load environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

# Initialize bot with commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Define an asynchronous function to load cogs
async def load_extensions():
    await bot.load_extension('cogs.general')
    await bot.load_extension('cogs.voice')
    await bot.load_extension('cogs.admin')

# Define the main function to run the bot
async def main():
    async with bot:
        await load_extensions()
        schedule_reboot(bot)
        await bot.start(DISCORD_BOT_TOKEN)

# Run the main function using asyncio.run
asyncio.run(main())
