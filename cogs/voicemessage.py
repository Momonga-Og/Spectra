import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import os

class VoiceMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def text_to_speech(self, text, filename):
        tts = gTTS(text)
        tts.save(filename)

    @app_commands.command(name='vm', description="Set a voice message for a user")
    async def vm(self, interaction: discord.Interaction, member: discord.Member, message: str):
        if not hasattr(self.bot.get_cog('Voice'), 'message_to_deliver'):
            await interaction.response.send_message("Voice greeting functionality is not set up properly.")
            return

        self.bot.get_cog('Voice').message_to_deliver[member.id] = message
        await interaction.response.send_message(f"Message set for {member.name}. Waiting for them to join a voice channel...")

async def setup(bot):
    cog = VoiceMessage(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.vm)
