import discord
from discord.ext import commands
import os
import asyncio
import logging
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

OWNER_ID = 486652069831376943  
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

LOCK_FILE = 'bot.lock'

# Function to check if the bot is already running
def check_lock():
    if os.path.exists(LOCK_FILE):
        logger.info("Bot is already running. Exiting...")
        sys.exit()

# Function to create a lock file
def create_lock():
    with open(LOCK_FILE, 'w') as f:
        f.write('locked')

# Function to remove the lock file
def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# Database setup: Initialize SQLite for conversation history
def init_db():
    db_path = 'conversation_history.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS conversation (user_id INTEGER, prompt TEXT, response TEXT)''')
    conn.commit()
    conn.close()

# Initialize database on bot start
init_db()

def read_memory_file():
    logger.info("Attempting to read memory.txt...")
    try:
        with open('memory.txt', 'r') as f:
            content = f.read()
            logger.info("Memory file read successfully.")
            return content
    except FileNotFoundError:
        logger.error("Memory file not found.")
        return None
    except Exception as e:
        logger.error(f"An error occurred while reading the memory file: {e}")
        return None

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    await sync_commands()

async def sync_commands():
    if not hasattr(bot, 'synced'):
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} commands")
            bot.synced = True
        except Exception as e:
            logger.exception("Failed to sync commands")

@bot.command(name='memory')
async def memory_command(ctx):
    memory_content = read_memory_file()
    if memory_content:
        await ctx.send(f"Memory:\n```\n{memory_content}\n```")
    else:
        await ctx.send("Could not read memory.")

@bot.event
async def on_message(message: discord.Message):
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        await forward_dm(message)
    await bot.process_commands(message)

async def forward_dm(message: discord.Message):
    owner = await bot.fetch_user(OWNER_ID)
    if owner:
        await owner.send(f"Message from {message.author}: {message.content}")

@bot.event
async def on_disconnect():
    logger.info("Bot disconnected")

@bot.event
async def on_error(event: str, *args, **kwargs):
    logger.exception(f"An error occurred in event {event}")

@bot.event
async def on_close():
    logger.info("Bot is closing")
    await close_sessions()

EXTENSIONS = [
    'cogs.general', 'cogs.moderation', 'cogs.poll', 'cogs.admin',
    'cogs.relocate', 'cogs.watermark', 'cogs.serverstats', 'cogs.talk', 'cogs.write',
    'cogs.watermark_user', 'cogs.attack', 'cogs.role', 'cogs.metiers',
    'cogs.youtube_mp3', 'cogs.image_converter', 'cogs.clear', 'cogs.startguild',  # Corrected here
    'cogs.rbg', 'cogs.bow', 'cogs.welcomesparta', 'cogs.contract', 'cogs.profession',
    'cogs.super', 'cogs.ai', 'cogs.translator', 'cogs.spotify', 'cogs.voice', 'cogs.youtubemp4',
]


async def load_extensions():
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            logger.exception(f"Failed to load extension {extension}")

async def main():
    check_lock()  # Check for existing lock
    create_lock()  # Create a lock file

    async with bot:
        await load_extensions()
        if not TOKEN:
            logger.error("Bot token not found")
            return
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            logger.error("Invalid token")
        except Exception as e:
            logger.exception("Failed to start the bot")
        finally:
            remove_lock()  # Ensure lock is removed when done

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        remove_lock()  # Clean up on exit
    except Exception as e:
        logger.exception("Bot encountered an error and stopped")
        remove_lock()  # Clean up on error
