import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
import logging
import random
import speech_recognition as sr
from transformers import pipeline
import tempfile

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

    def text_to_speech(self, text):
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name

    def generate_ai_response(self, text):
        response = self.conversation_pipeline(text)
        return response[0]["generated_text"]

    async def connect_to_channel(self, channel, retries=3, delay=5):
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
                        welcome_text = random.choice(self.welcome_messages).format(name=member.name)
                        audio_file = self.text_to_speech(welcome_text)

                        # Play welcome message
                        if not vc.is_playing():
                            vc.play(discord.FFmpegPCMAudio(audio_file))
                            while vc.is_playing():
                                await asyncio.sleep(1)

                        # Listen for user question
                        # Modify this part to work with audio files recorded from the voice channel
                        # e.g., Use voice channel recording instead of microphone
                        user_question = "Sample user question"  # Placeholder, replace with actual audio recognition logic
                        logging.info(f"Recognized question: {user_question}")

                        # Generate AI response
                        ai_response = self.generate_ai_response(user_question)
                        logging.info(f"AI response: {ai_response}")

                        # Convert AI response to speech and play
                        response_audio = self.text_to_speech(ai_response)
                        vc.play(discord.FFmpegPCMAudio(response_audio))

                        # Disconnect after playing the response
                        while vc.is_playing():
                            await asyncio.sleep(1)

                        if vc.is_connected():
                            await vc.disconnect()

                        # Clean up audio files
                        os.remove(audio_file)
                        os.remove(response_audio)

                except Exception as e:
                    logging.exception(f"Error in on_voice_state_update: {e}")

    async def cog_unload(self):
        for vc in self.bot.voice_clients:
            await vc.disconnect()

async def setup(bot):
    await bot.add_cog(Voice(bot))
