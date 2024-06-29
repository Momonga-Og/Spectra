import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import logging

WELCOME_CONFIG_FILE = "welcome_config.json"

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = None
        self.load_welcome_channel()

    def load_welcome_channel(self):
        if os.path.exists(WELCOME_CONFIG_FILE):
            with open(WELCOME_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.welcome_channel_id = config.get('welcome_channel_id', None)
        else:
            self.welcome_channel_id = None

    def save_welcome_channel(self):
        with open(WELCOME_CONFIG_FILE, 'w') as f:
            json.dump({'welcome_channel_id': self.welcome_channel_id}, f)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.welcome_channel_id is None:
            logging.info("Welcome channel is not set.")
            return

        welcome_channel = self.bot.get_channel(self.welcome_channel_id)
        if welcome_channel is not None:
            await welcome_channel.send(f"Welcome to the server, {member.mention}!")
        else:
            logging.warning("Welcome channel not found!")

    @app_commands.command(name="setwelcomechannel", description="Set the channel for welcome messages.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="The channel to send welcome messages to")
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.welcome_channel_id = channel.id
        self.save_welcome_channel()
        await interaction.response.send_message(f"Welcome channel set to {channel.mention}", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"WelcomeCog is ready. Welcome channel ID: {self.welcome_channel_id}")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
