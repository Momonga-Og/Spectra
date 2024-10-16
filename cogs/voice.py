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
from googletrans import Translator  # Import for multilingual support

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
        self.translator = Translator()
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
                        # Welcome message
                        welcome_text = random.choice(self.welcome_messages).format(name=member.name)
                        audio_file = self.text_to_speech(welcome_text)
                        
                        # Play welcome message
                        if not vc.is_playing():
                            vc.play(discord.FFmpegPCMAudio(audio_file))
                            while vc.is_playing():
                                await asyncio.sleep(1)
                        
                        # Listen for user question
                        user_question = "What is the capital of France?"  # Placeholder, replace with actual audio recognition logic
                        context = "France is a country in Europe. Paris is its capital city."  # Example context
                        logging.info(f"Recognized question: {user_question}")

                        # Translate question to English if necessary
                        translated_question = self.translator.translate(user_question, dest='en').text
                        
                        # Generate AI response using question-answering
                        ai_response = self.generate_ai_response(translated_question, context)
                        logging.info(f"AI response: {ai_response}")

                        # Log the interaction
                        self.log_interaction(user_question, ai_response)
                        
                        # Translate response back to user's language if necessary
                        translated_response = self.translator.translate(ai_response, dest=self.translator.detect(user_question).lang).text

                        # Convert AI response to speech and play
                        response_audio = self.text_to_speech(translated_response)
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
