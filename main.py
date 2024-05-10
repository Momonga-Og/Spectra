import discord
from gtts import gTTS
import os
import asyncio  
from discord.ext import commands
from discord import app_commands
  
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True  
intents.voice_states = True  

# Create the bot instance with desired intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Use the existing command tree from the bot
tree = bot.tree  # No need to create a new CommandTree

@tree.command(name='hello', description='Replies with Hello!')
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')

def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

# Event: when the bot is ready
@bot.event
async def on_ready():
    # Sync the command tree with Discord
    await tree.sync()  # Sync globally or specify a guild
    print(f'Logged in as {bot.user}')

# Event: when a member joins a voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        # Check if the bot is already connected to a voice channel
        if not bot.voice_clients:
            vc = await after.channel.connect()  # Join the voice channel
        else:
            vc = bot.voice_clients[0]  # Use the existing voice client

        # Prepare and play audio
        audio_file = f'{member.name}_welcome.mp3'
        welcome_text = f'Welcome to the voice channel, {member.name}!'
        text_to_speech(welcome_text, audio_file)

        vc.play(discord.FFmpegPCMAudio(audio_file))  # Play the audio
        
        # Wait until the audio is finished
        while vc.is_playing():
            await asyncio.sleep(1)

        # Disconnect after playing
        if vc.is_connected():
            await vc.disconnect()

        # Clean up the audio file after use
        os.remove(audio_file)

# Start the bot
bot.run(DISCORD_BOT_TOKEN)
