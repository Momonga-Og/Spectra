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
                        vc = await after.channel.connect(timeout=60)  # Increase timeout to 60 seconds
                    else:
                        vc = self.bot.voice_clients[0]
                        if vc.channel != after.channel:
                            await vc.move_to(after.channel)

                    if vc and vc.is_connected():
                        audio_file = f'{member.name}_welcome.mp3'
                        welcome_text = f'Welcome to the voice channel, {member.name}!'
                        self.text_to_speech(welcome_text, audio_file)

                        vc.play(discord.FFmpegPCMAudio(audio_file))

                        while vc.is_playing():
                            await asyncio.sleep(1)

                        if vc.is_connected():
                            await vc.disconnect()

                        # Clean up the audio file after use
                        os.remove(audio_file)
                    else:
                        logging.error("Failed to connect to voice channel.")
                except asyncio.TimeoutError:
                    logging.error("Failed to connect to voice channel due to timeout.")
                except AttributeError as attr_err:
                    logging.error(f"AttributeError in voice connection: {attr_err}")
                except Exception as e:
                    logging.exception(f"Error in on_voice_state_update: {e}")

    async def cog_unload(self):
        for vc in self.bot.voice_clients:
            await vc.disconnect()

async def setup(bot):
    cog = Voice(bot)
    await bot.add_cog(cog)

    @bot.command()
    async def unlock(ctx):
        await ctx.send("Unlock command executed")

    @bot.command()
    async def relocate(ctx, channel: discord.TextChannel, *, message):
        try:
            await message.delete()
            await ctx.send(f"Message relocated to {channel.mention}")
        except discord.errors.NotFound:
            await ctx.send("The message you are trying to delete was not found.")
        except Exception as e:
            logging.exception(f"Error in relocate command: {e}")
            await ctx.send("An error occurred while trying to relocate the message.")
