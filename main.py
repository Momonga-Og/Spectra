import discord
from discord.ext import commands
import os
import asyncio
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define intents for the bot
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Owner ID for administrative commands
OWNER_ID = 486652069831376943  # Your Discord ID for owner/admin commands
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# File name for conversation history
HISTORY_FILE = 'conversation_history.json'

# Initialize the conversation history file
def init_conversation_history():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)  # Start with an empty list
        logger.info("Initialized conversation history file.")

# Load conversation history from JSON file
def load_conversation_history():
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

# Save conversation history to JSON file
def save_conversation_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

# Initialize the conversation history on bot start
init_conversation_history()

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

@bot.event
async def on_message(message: discord.Message):
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        await forward_dm(message)
        await save_conversation(message)  # Save the conversation to JSON
    await bot.process_commands(message)

async def forward_dm(message: discord.Message):
    owner = await bot.fetch_user(OWNER_ID)
    if owner:
        await owner.send(f"Message from {message.author}: {message.content}")

async def save_conversation(message: discord.Message):
    history = load_conversation_history()
    entry = {
        "user_id": message.author.id,
        "prompt": message.content,
        "response": "N/A"  # Placeholder for response; you can modify this as needed
    }
    history.append(entry)
    save_conversation_history(history)
    logger.info("Saved conversation to history.")

@bot.event
async def on_disconnect():
    logger.info("Bot disconnected")

@bot.event
async def on_error(event: str, *args, **kwargs):
    logger.exception(f"An error occurred in event {event}")

@bot.event
async def on_close():
    logger.info("Bot is closing")

# Load cogs/extensions (you can add your cogs here)
EXTENSIONS = [
    'cogs.ai'  # Add any other cogs you have here
]

async def load_extensions():
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            logger.exception(f"Failed to load extension {extension}")

async def main():
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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("Bot encountered an error and stopped")
