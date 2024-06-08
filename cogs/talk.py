import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import os
import asyncio
import logging

class Talk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def text_to_speech(self, text, filename):
        tts = gTTS(text)
        tts.save(filename)

    @app_commands.command(name="talk", description="Make the bot say a message in a voice channel")
    async def talk(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(ephemeral=True)  # Defer the response to give time for processing

        # Find the voice channel the user is in
        voice_channel = None
        if interaction.user.voice:
            voice_channel = interaction.user.voice.channel
        else:
            await interaction.followup.send("You need to be in a voice channel to use this command.")
            return

        try:
            # Generate the audio file
            audio_file = 'message.mp3'
            self.text_to_speech(f"Message from {interaction.user.name}: {message}", audio_file)

            # Connect to the voice channel
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio(audio_file))

            while vc.is_playing():
                await asyncio.sleep(1)

            # Disconnect from the voice channel
            if vc.is_connected():
                await vc.disconnect()

            # Clean up the audio file after use
            os.remove(audio_file)

            await interaction.followup.send("Message delivered successfully.")
        except Exception as e:
            logging.exception(f"Error in talk command: {e}")
            await interaction.followup.send(f"An error occurred while processing your request: {e}")

async def setup(bot):
    cog = Talk(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.talk)
