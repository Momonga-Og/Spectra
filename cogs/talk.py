import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

class Talk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def text_to_speech(self, text, filename):
        tts = gTTS(text)
        tts.save(filename)

    @app_commands.command(name="talk", description="Make the bot say a message in the voice channel")
    async def talk(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()  # Defer the response to give time for processing

        user = interaction.user
        channel = user.voice.channel if user.voice else None

        if channel is None:
            await interaction.followup.send("You need to be in a voice channel to use this command.")
            return

        try:
            # Check for existing voice clients and connect/move as needed
            vc = None
            if not self.bot.voice_clients:
                vc = await channel.connect(timeout=60)  # Increase timeout to 60 seconds
            else:
                vc = self.bot.voice_clients[0]
                if vc.channel != channel:
                    await vc.move_to(channel)

            if vc and vc.is_connected():
                try:
                    announce_text = f"Message from {user.name}: {message}"
                    audio_file = f'{user.name}_talk.mp3'
                    self.text_to_speech(announce_text, audio_file)

                    vc.play(discord.FFmpegPCMAudio(audio_file))

                    while vc.is_playing():
                        await asyncio.sleep(1)

                    if vc.is_connected():
                        await vc.disconnect()

                    # Clean up the audio file after use
                    os.remove(audio_file)

                    await interaction.followup.send("Message sent successfully.")
                except Exception as e:
                    logging.exception(f"Error in talk command: {e}")
                    await interaction.followup.send(f"An error occurred: {e}")
            else:
                logging.error("Failed to connect to voice channel.")
                await interaction.followup.send("Failed to connect to the voice channel.")
        except asyncio.TimeoutError:
            logging.error("Failed to connect to voice channel due to timeout.")
            await interaction.followup.send("Failed to connect to the voice channel due to a timeout.")
        except Exception as e:
            logging.exception(f"Error in talk command: {e}")
            await interaction.followup.send(f"An error occurred: {e}")

async def setup(bot):
    cog = Talk(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('talk'):
        bot.tree.add_command(cog.talk)
