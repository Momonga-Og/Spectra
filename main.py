import discord
from discord.ext import commands
import os
import asyncio
import logging
from utils.scheduler import schedule_reboot

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

# Initialize bot with commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} commands")
    except Exception as e:
        logging.exception("Failed to sync commands")

@bot.event
async def on_disconnect():
    logging.info("Bot disconnected")

@bot.event
async def on_close():
    logging.info("Bot is closing")
    await bot.session.close()

# Define an asynchronous function to load cogs
async def load_extensions():
    try:
        await bot.load_extension('cogs.general')
        await bot.load_extension('cogs.moderation')
        await bot.load_extension('cogs.poll')
        await bot.load_extension('cogs.admin')
        await bot.load_extension('cogs.voice')
    except Exception as e:
        logging.exception("Failed to load extensions")

# Define the main function to run the bot
async def main():
    async with bot:
        await load_extensions()
        schedule_reboot(bot)
        await bot.start(DISCORD_BOT_TOKEN)

# Run the main function using asyncio.run
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Bot encountered an error and stopped")
