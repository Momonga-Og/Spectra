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
from deep_translator import GoogleTranslator  # Import for multilingual support
from langdetect import detect  # Import for language detection

logging.basicConfig(level=logging.INFO)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}
        self.welcome_messages = [
            "Hello there! Glad you could join us, {name}!",
            "Welcome, {name}! We hope you have a great time!",
        ]
        # Initialize the BERT question-answering model
        self.qa_pipeline = pipeline("question-answering", model="google-bert/bert-large-uncased-whole-word-masking-finetuned-squad")
        # Initialize translator for multilingual support
        self.translator = GoogleTranslator()
        # Initialize feedback logs
        self.feedback_log = []

    def text_to_speech(self, text, lang='en'):
        tts = gTTS(text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name

    def generate_ai_response(self, question, context):
        # Use the question-answering model to generate a response
        response = self.qa_pipeline(question=question, context=context)
        return response['answer']

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

    def log_interaction(self, question, ai_response):
        # Log the question and AI response for continuous learning
        self.feedback_log.append({'question': question, 'response': ai_response})
        logging.info(f"Logged interaction: Question: {question}, Response: {ai_response}")

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
                        # Check if the user joined the specific server (Clash of Champions Episode 1)
                        if guild_id == 1296795292703784960:
                            # Custom message for the Clash of Champions Episode 1 server
                            welcome_text = f"Hello {member.name}, welcome to {member.guild.name}. The Sheikh is very happy to have you here. Please have fun and be comfortable."
                        else:
                            # Generic message for other servers
                            welcome_text = random.choice(self.welcome_messages).format(name=member.name)

                        audio_file = self.text_to_speech(welcome_text)
                        
                        # Play welcome message
                        if not vc.is_playing():
                            vc.play(discord.FFmpegPCMAudio(audio_file))
                            while vc.is_playing():
                                await asyncio.sleep(1)
                        
                        # Disconnect after playing the response
                        if vc.is_connected():
                            await vc.disconnect()
                        
                        # Clean up audio files
                        os.remove(audio_file)
                except Exception as e:
                    logging.exception(f"Error in on_voice_state_update: {e}")

    async def cog_unload(self):
        for vc in self.bot.voice_clients:
            await vc.disconnect()

async def setup(bot):
    await bot.add_cog(Voice(bot))
