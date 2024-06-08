import discord
from discord.ext import commands
import os
import asyncio
import logging
import sys

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

async def close_sessions():
    await bot.session.close()

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    if not hasattr(bot, 'synced'):
        try:
            synced = await bot.tree.sync()
            logging.info(f"Synced {len(synced)} commands")
            bot.synced = True
        except Exception as e:
            logging.exception("Failed to sync commands")

@bot.event
async def on_disconnect():
    logging.info("Bot disconnected")

@bot.event
async def on_close():
    logging.info("Bot is closing")
    await close_sessions()

async def reboot_bot():
    logging.info("Rebooting bot")
    await bot.close()
    os.execl(sys.executable, sys.executable, *sys.argv)  # Restart the script

def schedule_reboot(bot):
    async def reboot_task():
        while True:
            await asyncio.sleep(18000)  # 5 hours
            await reboot_bot()

    bot.loop.create_task(reboot_task())

# Define an asynchronous function to load cogs
async def load_extensions():
    try:
        await bot.load_extension('cogs.general')
        await bot.load_extension('cogs.moderation')
        await bot.load_extension('cogs.poll')
        await bot.load_extension('cogs.admin')
        await bot.load_extension('cogs.voice')
        await bot.load_extension('cogs.relocate')
        await bot.load_extension('cogs.serverstats')
        await bot.load_extension('cogs.talk')
        await bot.load_extension('cogs.watermark')
        await bot.load_extension('cogs.voicemessage')  # Add this line
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
