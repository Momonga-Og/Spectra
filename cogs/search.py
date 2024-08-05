import discord
from discord.ext import commands
import os
import asyncio
import logging
import speech_recognition as sr
import requests
from bs4 import BeautifulSoup
from discord import FFmpegPCMAudio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def join_voice_channel(self, interaction):
        """Join the user's voice channel."""
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            vc = await channel.connect()
            return vc
        else:
            await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True)
            return None

    async def recognize_speech(self, audio_file):
        """Recognize speech from the audio file."""
        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            return f"Could not request results; {e}"

    async def search_google(self, query):
        """Perform a web search and return the top result."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract search results
        result = soup.find('div', class_='BNeawe vvjwJb AP7Wnd')
        if result:
            title = result.get_text()
            snippet = result.find_next('div', class_='BNeawe s3v9rd AP7Wnd').get_text()
            link = result.find_next('a')['href']
            return f"{title}\n{snippet}\nhttps://www.google.com{link}"
        else:
            return "No results found."

    @discord.app_commands.command(name='search', description="Join voice chat, listen to the user, and return search results.")
    async def search(self, interaction: discord.Interaction):
        """Join voice chat, listen to the user, and return search results."""
        vc = await self.join_voice_channel(interaction)
        if vc:
            audio_file = 'user_speech.wav'

            def save_audio():
                # Simulate recording audio from the voice channel
                # This would normally involve capturing the audio stream and saving it to a file
                pass

            await interaction.response.send_message("Please speak now...", ephemeral=True)
            await asyncio.sleep(5)
            save_audio()

            await vc.disconnect()

            recognized_text = await self.recognize_speech(audio_file)
            await interaction.followup.send(f"You said: {recognized_text}")

            search_result = await self.search_google(recognized_text)
            await interaction.followup.send(search_result)

            if os.path.exists(audio_file):
                os.remove(audio_file)

async def setup(bot):
    await bot.add_cog(Search(bot))
