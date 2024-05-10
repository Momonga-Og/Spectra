import discord
import os
import requests
import asyncio
from gtts import gTTS
from discord.ext import commands
from discord import app_commands
from bs4 import BeautifulSoup
import urllib.parse
import logging

# Discord bot token from environment variable
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up logging
logger = logging.getLogger("DiscordBot")
logging.basicConfig(level=logging.INFO)

# Set up intents for the bot
intents = discord.Intents.default()
intents.members = True  
intents.voice_states = True  
intents.message_content = True

# Create the bot instance with desired intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Custom Exceptions
class TooMuchCharactersException(Exception):
    pass

class NotFoundCharacterException(Exception):
    pass

class Character:
    def __init__(self, name, server, url):
        self.name = name
        self.server = server
        self.url = url

    @classmethod
    def get_character(cls, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise NotFoundCharacterException("Character page not accessible")
        soup = BeautifulSoup(response.text, 'html.parser')
        # Example data extraction, adjust selectors based on webpage structure
        name = soup.select_one("selector_for_name").text
        server = soup.select_one("selector_for_server").text
        return cls(name, server, url)

    def to_embed(self):
        embed = discord.Embed(title=self.name, description=f"Server: {self.server}", color=0x00ff00)
        # Add additional character details
        return embed

# Whois Command
class WhoisCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="whois")
    async def whois(self, ctx, character_name: str, server_name: str = None):
        base_url = "https://www.dofus-touch.com/en/mmorpg/community/directories/character-pages"
        params = {"text": urllib.parse.quote(character_name)}
        if server_name:
            params["character_homeserv[]"] = server_name
        
        query_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        try:
            response = requests.get(query_url)
            response.raise_for_status()  # Check for errors

            soup = BeautifulSoup(response.text, 'html.parser')
            characters = []

            # Example: extracting character data from the page
            for row in soup.select("selector_for_character_rows"):
                name = row.select_one("selector_for_name").text.lower()
                if name == character_name.lower():
                    server = row.select_one("selector_for_server").text
                    url = row.select_one("a")["href"]
                    characters.append(Character(name, server, url))

            if not characters:
                raise NotFoundCharacterException("Character not found")
            elif len(characters) > 1:
                raise TooMuchCharactersException("Too many characters found")

            # If a single character is found
            character = characters[0]
            character_data = Character.get_character(character.url)
            await ctx.send(embed=character_data.to_embed())

        except requests.exceptions.RequestException as e:
            logger.error("HTTP Request failed: %s", e)
            await ctx.send("Error fetching character information.")
        except NotFoundCharacterException as e:
            await ctx.send(e.message)
        except TooMuchCharactersException as e:
            await ctx.send(e.message)

# Add the WhoisCommand cog to the bot
bot.add_cog(WhoisCommand(bot))

# Additional commands and event handlers

@bot.tree.command(name='hello', description='Replies with Hello!')
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')

@bot.tree.command(name='pm_all', description='Send a private message to all users in the server')
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

    await interaction.followup.send(
        f"Sent messages to {sent_count} users. Failed to send to {failed_count} users."
    )

@bot.tree.command(name='time', description='Get the current time in a specified city or country')
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

@bot.event
async def on_ready():
    # Sync command tree with Discord
    try:
        await tree.sync()  # Sync globally or for specific guild
        print(f'Logged in as {bot.user}')
    except Exception as e:
        print(f"Error during command sync: {e}")

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

def text_to_speech(text, file_path):
    tts = gTTS(text)
    tts.save(file_path)

# Start the bot
bot.run(DISCORD_BOT_TOKEN)
