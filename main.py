import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

# Create a bot with a command prefix
bot = commands.Bot(command_prefix='/', intents=intents)

# Function to create TTS audio
def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

# Event: when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Command: Display list of available commands
@bot.command(name="commands")
async def show_commands(ctx):
    # Determine if the context is a DM or a text channel
    if ctx.guild is None:
        # It's a DM
        await ctx.send("You're in a DM. Here are the commands:")
    else:
        # It's a text channel
        await ctx.send("You're in a text channel. Here are the commands:")

    commands_text = """
    Available commands:
/commands - Show this list of commands
/stop - Stop the bot's current operation
/work - Resume the bot's automatic functions
    """
    await ctx.send(commands_text)

# Command: /stop to stop the bot's operations
is_stopped = False

@bot.command()
async def stop(ctx):
    global is_stopped
    is_stopped = True
    await ctx.send("Bot operations stopped.")

# Command: /work to resume automatic functions (works if stopped)
@bot.command()
async def work(ctx):
    global is_stopped
    if is_stopped:
        is_stopped = False
        await ctx.send("Bot operations resumed.")
    else:
        await ctx.send("Bot is already running.")

# Start the bot
bot.run(DISCORD_BOT_TOKEN)
