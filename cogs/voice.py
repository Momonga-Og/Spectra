import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}

    def text_to_speech(self, text, filename):
        tts = gTTS(text)
        tts.save(filename)

    async def connect_to_channel(self, channel, retries=3, delay=5):
        """Attempts to connect to a voice channel with retries."""
        for attempt in range(retries):
            try:
                vc = await channel.connect()
                return vc
            except asyncio.TimeoutError as e:
                logging.warning(f"TimeoutError while connecting to voice channel, attempt {attempt + 1} of {retries}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise e

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            guild_id = member.guild.id
            if guild_id not in self.blocked_users:
                self.blocked_users[guild_id] = set()
            
            if not member.bot and member.id not in self.blocked_users[guild_id]:
                try:
                    # Check for existing voice clients and connect/move as needed
                    vc = None
                    if not self.bot.voice_clients:
                        vc = await self.connect_to_channel(after.channel)
                    else:
                        vc = self.bot.voice_clients[0]
                        if vc.channel != after.channel:
                            await vc.move_to(after.channel)

                    audio_file = f'{member.name}_welcome.mp3'
                    welcome_text = f'Welcome to the voice channel, {member.name}!'
                    self.text_to_speech(welcome_text, audio_file)

                    # Ensure we're not already playing something
                    if not vc.is_playing():
                        vc.play(discord.FFmpegPCMAudio(audio_file))

                        while vc.is_playing():
                            await asyncio.sleep(1)

                    # Disconnect after playing the welcome message
                    if vc.is_connected():
                        await vc.disconnect()

                    # Check if the audio file exists before trying to remove it
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                    else:
                        logging.warning(f"Audio file {audio_file} not found for removal.")
                except discord.errors.ClientException as e:
                    logging.exception(f"ClientException in on_voice_state_update: {e}")
                except discord.errors.DiscordException as e:
                    logging.exception(f"DiscordException in on_voice_state_update: {e}")
                except asyncio.TimeoutError as e:
                    logging.exception(f"TimeoutError in on_voice_state_update: {e}")
                except Exception as e:
                    logging.exception(f"Unexpected error in on_voice_state_update: {e}")

    async def cog_unload(self):
        for vc in self.bot.voice_clients:
            await vc.disconnect()

async def setup(bot):
    await bot.add_cog(Voice(bot))
