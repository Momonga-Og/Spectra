import discord
from discord.ext import commands
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

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

async def load_extensions():
    try:
        await bot.load_extension('cogs.general')
        await bot.load_extension('cogs.moderation')
        await bot.load_extension('cogs.poll')
        await bot.load_extension('cogs.admin')
        await bot.load_extension('cogs.voice')
        await bot.load_extension('cogs.relocate')
        await bot.load_extension('cogs.watermark')
        await bot.load_extension('cogs.serverstats')
        await bot.load_extension('cogs.talk')
    except Exception as e:
        logging.exception("Failed to load extensions")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logging.error("Bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
            return
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Bot encountered an error and stopped")
