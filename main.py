import discord
from discord.ext import commands
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Replace 'YOUR_USER_ID' with your actual Discord user ID
OWNER_ID = 486652069831376943  # Example ID, replace with your actual Discord user ID

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
async def on_message(message):
    # Check if the message is a DM and not from the bot itself
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        # Get the owner (you)
        owner = await bot.fetch_user(OWNER_ID)
        if owner:
            # Forward the message content to the owner
            await owner.send(f"Message from {message.author}: {message.content}")

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
        await bot.load_extension('cogs.write')
        await bot.load_extension('cogs.watermark_user')
        await bot.load_extension('cogs.attack')  # Added attack extension
        await bot.load_extension('cogs.new_users')  # Added new_users extension
        await bot.load_extension('cogs.role')
        await bot.load_extension('cogs.panel')
        await bot.load_extension('cogs.youtube_mp3')
        await bot.load_extension('cogs.image_converter')
        await bot.load_extension('cogs.clear')
        await bot.load_extension('cogs.screenshot')
        await bot.load_extension('cogs.rbg')
        await bot.load_extension('cogs.resize')



    except Exception as e:
        logging.exception("Failed to load extensions")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logging.error("Bot token not found")
            return
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Bot encountered an error and stopped")
