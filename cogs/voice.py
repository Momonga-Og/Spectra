import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
import logging
import random
import speech_recognition as sr
from transformers import pipeline  # For AI-based responses

logging.basicConfig(level=logging.INFO)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}
        self.welcome_messages = [
            "Hello there! Glad you could join us, {name}!",
            "Welcome, {name}! We hope you have a great time!",
        ]
        self.conversation_pipeline = pipeline("text2text-generation", model="facebook/blenderbot-400M-distill")

    def text_to_speech(self, text, filename):
        tts = gTTS(text)
        tts.save(filename)

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for a question...")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Sorry, I didn't catch that."
            except sr.RequestError:
                return "Speech Recognition service is unavailable."

    def generate_ai_response(self, text):
        response = self.conversation_pipeline(text)
        return response[0]["generated_text"]

    async def connect_to_channel(self, channel, retries=3, delay=5):
        """Attempts to connect to a voice channel with retries."""
        for attempt in range(retries):
            try:
                vc = await channel.connect()
                return vc
            except (asyncio.TimeoutError, discord.errors.ConnectionClosed) as e:
                logging.warning(f"Error while connecting to voice channel, attempt {attempt + 1} of {retries}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise e
        return None

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            guild_id = member.guild.id
            if guild_id not in self.blocked_users:
                self.blocked_users[guild_id] = set()

            if not member.bot and member.id not in self.blocked_users[guild_id]:
                try:
                    vc = await self.connect_to_channel(after.channel)
                    
                    if vc and vc.is_connected():
                        # Welcome message
                        audio_file = f'{member.name}_welcome.mp3'
                        welcome_text = random.choice(self.welcome_messages).format(name=member.name)
                        self.text_to_speech(welcome_text, audio_file)

                        # Play welcome message
                        if not vc.is_playing():
                            vc.play(discord.FFmpegPCMAudio(audio_file))
                            while vc.is_playing():
                                await asyncio.sleep(1)

                        # Listen for user question after welcome
                        user_question = self.recognize_speech()
                        logging.info(f"Recognized question: {user_question}")

                        # Generate AI response
                        ai_response = self.generate_ai_response(user_question)
                        logging.info(f"AI response: {ai_response}")

                        # Convert AI response to speech and play
                        response_audio = f'{member.name}_response.mp3'
                        self.text_to_speech(ai_response, response_audio)
                        vc.play(discord.FFmpegPCMAudio(response_audio))

                        # Disconnect after playing the response
                        while vc.is_playing():
                            await asyncio.sleep(1)

                        if vc.is_connected():
                            await vc.disconnect()

                        # Clean up audio files
                        if os.path.exists(audio_file):
                            os.remove(audio_file)
                        if os.path.exists(response_audio):
                            os.remove(response_audio)

                except Exception as e:
                    logging.exception(f"Error in on_voice_state_update: {e}")

    async def cog_unload(self):
        for vc in self.bot.voice_clients:
            await vc.disconnect()

async def setup(bot):
    await bot.add_cog(Voice(bot))
