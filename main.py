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

# Global variable to track the stopped state
is_stopped = False

# Function to create TTS audio
def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

# Event: when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Event: when a member joins a voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    # If the bot is stopped, do nothing
    if is_stopped:
        return

    if before.channel is None and after.channel is not None:
        # If the bot isn't already in a voice channel
        if not bot.voice_clients:
            vc = await after.channel.connect()
        else:
            vc = bot.voice_clients[0]

        # Play the welcome message
        audio_file = f'{member.name}_welcome.mp3'
        welcome_text = f'Welcome to the voice channel, {member.name}!'
        text_to_speech(welcome_text, audio_file)

        vc.play(discord.FFmpegPCMAudio(audio_file))

        # Wait until the audio is finished
        while vc.is_playing():
            await asyncio.sleep(1)

        # Disconnect after playing
        if vc.is_connected():
            await vc.disconnect()

        # Clean up the audio file after use
        os.remove(audio_file)

# Command: /commands to show available commands
@bot.command(name="commands")
async def show_commands(ctx):
    commands_text = """
    Available commands:
/commands - Show this list of commands
/stop - Stop the bot's current operation
/work - Resume the bot's automatic functions
    """
    await ctx.send(commands_text)

# Command: /stop to stop the bot's operations
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
