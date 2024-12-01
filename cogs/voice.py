import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
import logging
import random
import tempfile

logging.basicConfig(level=logging.INFO)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}
        self.welcome_messages_en = [
            "Hello there! Glad you could join us, {name}!",
            "Welcome, {name}! We hope you have a great time!",
        ]
        self.welcome_messages_fr = [
            "Bonjour {name}! Ravi de vous avoir parmi nous.",
            "Bienvenue, {name}! Nous espérons que vous passerez un bon moment.",
        ]

    def text_to_speech(self, text, lang='en'):
        """Converts text to speech in the specified language."""
        tts = gTTS(text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name

    async def connect_to_channel(self, channel, retries=3, delay=5):
        """Connects to a voice channel with retry logic."""
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
        """Triggers when a user joins a voice channel."""
        if before.channel is None and after.channel is not None:
            guild_id = member.guild.id
            if guild_id not in self.blocked_users:
                self.blocked_users[guild_id] = set()
            if not member.bot and member.id not in self.blocked_users[guild_id]:
                try:
                    vc = await self.connect_to_channel(after.channel)
                    if vc and vc.is_connected():
                        # Determine the greeting language and message
                        if guild_id == 1300093554064097400:  # French server
                            welcome_text = random.choice(self.welcome_messages_fr).format(name=member.name)
                            lang = 'fr'
                        else:  # Default to English
                            welcome_text = random.choice(self.welcome_messages_en).format(name=member.name)
                            lang = 'en'

                        # Convert text to speech
                        audio_file = self.text_to_speech(welcome_text, lang=lang)

                        # Play the welcome message
                        if not vc.is_playing():
                            vc.play(discord.FFmpegPCMAudio(audio_file))
                            while vc.is_playing():
                                await asyncio.sleep(1)

                        # Disconnect after playing the response
                        if vc.is_connected():
                            await vc.disconnect()

                        # Clean up the temporary audio file
                        os.remove(audio_file)
                except Exception as e:
                    logging.exception(f"Error in on_voice_state_update: {e}")

    async def cog_unload(self):
        """Disconnects all voice clients when the cog is unloaded."""
        for vc in self.bot.voice_clients:
            await vc.disconnect()

async def setup(bot):
    """Adds the Voice cog to the bot."""
    await bot.add_cog(Voice(bot))
