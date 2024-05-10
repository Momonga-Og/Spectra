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
intents.message_content = True  # Add this to avoid warnings

# Create the bot instance with desired intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Use the existing command tree from the bot
tree = bot.tree

@tree.command(name='hello', description='Replies with Hello!')
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')

@tree.command(name='pm_all', description='Send a private message to all users in the server')
@app_commands.describe(message='The message to send')
async def pm_all(interaction: discord.Interaction, message: str):
    # Check permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Acknowledge the command to avoid timeout
    await interaction.response.defer(ephemeral=True)  # Defers response but keeps interaction active

    sent_count = 0
    failed_count = 0
    guild = interaction.guild

    for member in guild.members:
        if member.bot or member == interaction.user:
            continue

        try:
            await member.send(message)  # Send a private message
            sent_count += 1
        except Exception:
            failed_count += 1

    # Send the final message indicating the results
    await interaction.followup.send(
        f"Sent messages to {sent_count} users. Failed to send to {failed_count} users."
    )

def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

# Event: when the bot is ready
@bot.event
async def on_ready():
    # Sync the command tree with Discord
    try:
        await tree.sync()  # Sync globally or specify a guild
        print(f'Logged in as {bot.user}')
    except Exception as e:
        print(f"Error during command sync: {e}")

# Event: when a member joins a voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        # Join the voice channel if the bot is not connected
        if not bot.voice_clients:
            vc = await after.channel.connect()
        else:
            vc = bot.voice_clients[0]

        # Prepare and play audio
        audio_file = f'{member.name}_welcome.mp3'
        welcome_text = f'Welcome to the voice channel, {member.name}!'
        text_to_speech(welcome_text, audio_file)

        vc.play(discord.FFmpegPCMAudio(audio_file))  # Play the audio
        
        while vc.is_playing():
            await asyncio.sleep(1)  # Wait until the audio is finished

        # Disconnect after playing
        if vc.is_connected():
            await vc.disconnect()

        # Clean up the audio file after use
        os.remove(audio_file)

# Start the bot
bot.run(DISCORD_BOT_TOKEN)
