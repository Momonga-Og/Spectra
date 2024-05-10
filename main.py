import discord
import os
import requests
import asyncio
from gtts import gTTS
from discord.ext import commands
from discord import app_commands
  
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Add this to get weather info

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

# Command to get the weather for a specified location
@tree.command(name='weather', description='Get the weather for a specified city or country')
@app_commands.describe(location='City or country to get the weather for')
async def weather_command(interaction: discord.Interaction, location: str):
    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        response.raise_for_status()  # Check for HTTP errors
        weather_data = response.json()

        city = weather_data['name']
        weather_desc = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']

        await interaction.response.send_message(
            f"Weather in {city}: {weather_desc}, {temperature}°C"
        )
    except requests.exceptions.HTTPError:
        await interaction.response.send_message("Could not find the specified location. Please check the spelling or try another location.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

# Event: when the bot is ready
@bot.event
async def on_ready():
    # Sync command tree with Discord
    try:
        await tree.sync()  # Sync globally or for specific guild
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
