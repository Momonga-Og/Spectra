import discord
from discord.ext import commands
import os
import asyncio
import logging
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def join_voice_channel(self, ctx):
        """Join the user's voice channel."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            vc = await channel.connect()
            return vc
        else:
            await ctx.send("You are not connected to a voice channel.")
            return None

    async def recognize_speech(self, audio_file):
        """Recognize speech from the audio file."""
        recognizer = sr.Recognizer()
        audio = AudioSegment.from_file(audio_file)
        play(audio)

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
        """Search Google for the query and return the top result."""
        api_key = 'YOUR_GOOGLE_API_KEY'
        search_engine_id = 'YOUR_SEARCH_ENGINE_ID'
        url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}'

        response = requests.get(url)
        results = response.json()

        if 'items' in results:
            first_result = results['items'][0]
            title = first_result['title']
            snippet = first_result['snippet']
            link = first_result['link']
            return f"{title}\n{snippet}\n{link}"
        else:
            return "No results found."

    @commands.slash_command(name='search', description="Join voice chat, listen to the user, and return search results.")
    async def search(self, ctx):
        """Join voice chat, listen to the user, and return search results."""
        vc = await self.join_voice_channel(ctx)
        if vc:
            audio_file = 'user_speech.wav'

            def save_audio():
                stream = discord.FFmpegPCMAudio(source=vc.source)
                audio = AudioSegment.from_raw(stream, sample_width=2, frame_rate=44100, channels=2)
                audio.export(audio_file, format='wav')

            await ctx.send("Please speak now...")
            await asyncio.sleep(5)
            save_audio()

            await vc.disconnect()

            recognized_text = await self.recognize_speech(audio_file)
            await ctx.send(f"You said: {recognized_text}")

            search_result = await self.search_google(recognized_text)
            await ctx.send(search_result)

            if os.path.exists(audio_file):
                os.remove(audio_file)

async def setup(bot):
    bot.add_cog(Search(bot))

