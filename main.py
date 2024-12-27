import discord
from discord.ext import commands, tasks
import os
import asyncio
import logging
import sqlite3
import sys
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

OWNER_ID = 486652069831376943  # Replace with your Discord user ID
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

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    change_status.start()
    await sync_commands()

async def sync_commands():
    if not hasattr(bot, 'synced'):
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} commands")
            bot.synced = True
        except Exception as e:
            logger.exception("Failed to sync commands")

status_messages = [
    "غا الغبرة والشراب و تفاح و البنان و الخس كي القنية,
    "وترري ترري مع بنة تمارة أويلي بغيت ليك الدل,
    "غانكولها ليك بطالينية توبا موروزا نونا اموريا",
]

@tasks.loop(minutes=10)
async def change_status():
    new_status = random.choice(status_messages)
    await bot.change_presence(activity=discord.Game(new_status))

@bot.command(name='joke')
async def tell_joke(ctx):
    jokes = [
        "Why don't skeletons fight each other? They don't have the guts!",
        "What do you call cheese that's not yours? Nacho cheese!",
        "Why couldn't the bicycle stand up by itself? It was two tired!"
    ]
    await ctx.send(random.choice(jokes))

@bot.command(name='fun_fact')
async def fun_fact(ctx):
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!",
        "Octopuses have three hearts.",
        "Bananas are berries, but strawberries aren't!"
    ]
    await ctx.send(random.choice(facts))

@bot.command(name='about_me')
async def about_me(ctx):
    await ctx.send("I'm your friendly bot, here to assist and entertain!")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}! We're glad to have you.")

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

EXTENSIONS = [
    'cogs.general', 'cogs.moderation', 'cogs.poll', 'cogs.admin', 'cogs.gtoguild', 'cogs.save', 'cogs.key', 'cogs.link',
    'cogs.relocate', 'cogs.watermark', 'cogs.serverstats', 'cogs.talk', 'cogs.write', 'cogs.alerts',
    'cogs.watermark_user', 'cogs.attack', 'cogs.role', 'cogs.metiers', 'cogs.percopos',
    'cogs.youtube_mp3', 'cogs.image_converter', 'cogs.clear', 'cogs.startguild', 'cogs.percoattack',
    'cogs.rbg', 'cogs.bow', 'cogs.welcomesparta', 'cogs.contract', 'cogs.profession',
    'cogs.super','cogs.translator', 'cogs.spotify', 'cogs.voice', 'cogs.youtubemp4',
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
