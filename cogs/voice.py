import discord
from discord.ext import commands
from gtts import gTTS
import os
import asyncio
import logging
import random

logging.basicConfig(level=logging.INFO)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}
        self.welcome_messages = [
            "Hello there! Glad you could join us, {name}!",
            "Welcome, {name}! We hope you have a great time!",
            "Hi {name}! Nice to see you here!",
            "Hey {name}! Welcome to the voice chat!",
            "Greetings, {name}! Enjoy your stay!",
            "What's up, {name}? Welcome aboard!",
            "Good to see you, {name}! Have fun!",
            "Hey {name}! Let's have a great time together!",
            "Welcome {name}! We're glad you're here!",
            "Hello {name}! Delighted to see you in the voice chat channel!"
        ]

    def text_to_speech(self, text, filename):
        tts = gTTS(text)
        tts.save(filename)

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
                    # Check for existing voice clients and connect/move as needed
                    vc = None
                    if not self.bot.voice_clients:
                        vc = await self.connect_to_channel(after.channel)
                    else:
                        vc = self.bot.voice_clients[0]
                        if vc.channel != after.channel:
                            await vc.move_to(after.channel)
                            vc = self.bot.voice_clients[0]

                    if vc and vc.is_connected():
                        audio_file = f'{member.name}_welcome.mp3'
                        welcome_text = random.choice(self.welcome_messages).format(name=member.name)
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
                    else:
                        logging.error("Failed to connect to the voice channel after retries.")
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

async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    bot.load_extension('your_cog_module_name')  # Replace with the actual module name

    await bot.start('your_token_here')  # Replace with your bot token

if __name__ == "__main__":
    asyncio.run(main())
