import discord
from discord.ext import commands, tasks
import os
import asyncio
import logging
import sqlite3
import sys
import random
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot intents and initialization
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # For personalized greetings

bot = commands.Bot(command_prefix='!', intents=intents)
OWNER_ID = 486652069831376943  # Replace with your actual Discord ID
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
LOCK_FILE = 'bot.lock'

# Dynamic statuses
STATUSES = [
    "Making virtual friends...",
    "Debugging myself...",
    "Listening to your secrets...",
    "Calculating pi...",
    "Spying on the server next door...",
    "Living the bot life!",
]

@tasks.loop(minutes=10)
async def change_status():
    await bot.change_presence(activity=discord.Game(random.choice(STATUSES)))

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

# Database setup
DB_PATH = 'conversation_history.db'
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS conversation (user_id INTEGER, prompt TEXT, response TEXT)''')
    conn.commit()
    conn.close()

# Initialize database on bot start
init_db()

# Read memory file
def read_memory_file():
    try:
        with open('memory.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "No memories yet."
    except Exception as e:
        logger.error(f"Error reading memory file: {e}")
        return "Error reading memory file."

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    await sync_commands()
    change_status.start()

# Sync commands
async def sync_commands():
    if not hasattr(bot, 'synced'):
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} commands")
            bot.synced = True
        except Exception as e:
            logger.exception("Failed to sync commands")

# Easter egg command
@bot.command(name='joke')
async def joke(ctx):
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        "I told my code a joke... but it didn't respond. Must be a silent loop."
    ]
    await ctx.send(random.choice(jokes))

# Personalized greetings
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')  # Adjust the channel name
    if channel:
        await channel.send(f"Welcome, {member.mention}! We're so glad you're here. Don't worry, I don't bite (often).")

# DM forwarding with humor
@bot.event
async def on_message(message: discord.Message):
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        await forward_dm(message)
    await bot.process_commands(message)

async def forward_dm(message: discord.Message):
    owner = await bot.fetch_user(OWNER_ID)
    if owner:
        await owner.send(f"📩 DM from {message.author} ({message.author.id}): {message.content}")

# Command to display memory
@bot.command(name='memory')
async def memory_command(ctx):
    memory_content = read_memory_file()
    await ctx.send(f"Memory:
```
{memory_content}
```" if memory_content else "Memory is blank!")

# Easter egg for bot personality
@bot.command(name='about_me')
async def about_me(ctx):
    await ctx.send("I'm a highly intelligent bot who's really good at pretending to be busy.")

# Poll feature
@bot.command(name='poll')
async def poll(ctx, *, question):
    message = await ctx.send(f"📊 Poll: {question}\nReact with 👍 for Yes or 👎 for No.")
    await message.add_reaction('👍')
    await message.add_reaction('👎')

# Fun fact command
@bot.command(name='fun_fact')
async def fun_fact(ctx):
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3000 years old!",
        "The Eiffel Tower can be 15 cm taller during the summer due to heat expansion.",
        "Octopuses have three hearts, and two of them stop beating when they swim."
    ]
    await ctx.send(random.choice(facts))

# Extension loader
EXTENSIONS = [
    'cogs.general', 'cogs.moderation', 'cogs.poll', 'cogs.admin', 'cogs.fun', 'cogs.utilities'
]

async def load_extensions():
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            logger.exception(f"Failed to load extension {extension}")

# Main bot loop
async def main():
    check_lock()
    create_lock()

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
            remove_lock()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        remove_lock()
    except Exception as e:
        logger.exception("Bot encountered an error and stopped")
        remove_lock()
