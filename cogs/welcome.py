import discord
from discord.ext import commands
from discord import app_commands
import logging

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = None  # Set this to your desired welcome channel ID
        self.bot.welcome_channel_id = self.welcome_channel_id

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.info(f"Member joined: {member.name} (ID: {member.id})")
        if self.welcome_channel_id is None:
            logging.info("Welcome channel is not set.")
            return

        welcome_channel = self.bot.get_channel(self.welcome_channel_id)
        if welcome_channel is not None:
            logging.info(f"Sending welcome message to channel: {welcome_channel.name}")
            await welcome_channel.send(f"Welcome to the server, {member.mention}!")
        else:
            logging.warning("Welcome channel not found!")

    @app_commands.command(name="setwelcomechannel", description="Set the channel for welcome messages.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="The channel to send welcome messages to")
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.welcome_channel_id = channel.id
        self.bot.welcome_channel_id = self.welcome_channel_id
        await interaction.response.send_message(f"Welcome channel set to {channel.mention}", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"WelcomeCog is ready. Welcome channel ID: {self.welcome_channel_id}")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
