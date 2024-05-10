import discord
import os
import requests
import asyncio
from gtts import gTTS
from discord.ext import commands
from discord import app_commands
  
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True  
intents.voice_states = True  
intents.message_content = True  # To handle message-related commands

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
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Defer response to prevent interaction timeout
    await interaction.response.defer(ephemeral=True)

    sent_count = 0
    failed_count = 0
    guild = interaction.guild

    for member in guild.members:
        if member.bot or member == interaction.user:
            continue

        try:
            await member.send(message)
            sent_count += 1
        except Exception:
            failed_count += 1

    # Send the final message indicating the results
    await interaction.followup.send(
        f"Sent messages to {sent_count} users. Failed to send to {failed_count} users."
    )

# Command to get the current time in a specified city or country
@tree.command(name='time', description='Get the current time in a specified city or country')
@app_commands.describe(location='City or country to get the time for')
async def time_command(interaction: discord.Interaction, location: str):
    try:
        response = requests.get(f"http://worldtimeapi.org/api/timezone/{location}")
        response.raise_for_status()  # Check for errors in response
        time_data = response.json()

        current_time = time_data['datetime']
        timezone = time_data['timezone']

        await interaction.response.send_message(f"Current time in {timezone}: {current_time}")
    except requests.exceptions.HTTPError:
        await interaction.response.send_message("Could not find the specified location. Please check the spelling or try another location.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

client = discord.Client(intents=intents)


def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

# Event: when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Event: when a member joins a voice channel
@client.event
async def on_voice_state_update(member, before, after):
    # Ensure the bot isn't already connected before joining a voice channel
    if before.channel is None and after.channel is not None:
        # Check if the bot is already connected to a voice channel
        if not client.voice_clients:
            vc = await after.channel.connect()  # Join the voice channel
        else:
            vc = client.voice_clients[0]  # Use the existing voice client

        # Play the audio file
        audio_file = f'{member.name}_welcome.mp3'
        welcome_text = f'Welcome to the voice channel, {member.name}!'
        text_to_speech(welcome_text, audio_file)

        vc.play(discord.FFmpegPCMAudio(audio_file))  # Play the audio
        
        # Wait until the audio is finished
        while vc.is_playing():
            await asyncio.sleep(1)  # Wait until the audio is done

        # Disconnect after playing
        if vc.is_connected():
            await vc.disconnect()  # Disconnect from the voice channel

        # Clean up the audio file after use
        # os.remove(audio_file)



# Start the bot
bot.run(DISCORD_BOT_TOKEN)
