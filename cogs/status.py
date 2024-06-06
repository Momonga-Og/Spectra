import discord
from discord.ext import commands
from discord import app_commands

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(app_commands.Command(
            name="status",
            description="Check the bot's status",
            callback=self.status
        ))
        await self.bot.tree.sync()

    async def status(self, interaction: discord.Interaction):
        try:
            # Check the bot's latency
            latency = self.bot.latency
            # Check if bot is connected to any voice channel
            voice_connected = any(vc.is_connected() for vc in self.bot.voice_clients)
            
            status_message = (
                f"Bot is running.\n"
                f"Latency: {latency*1000:.2f} ms\n"
                f"Connected to voice channel: {'Yes' if voice_connected else 'No'}"
            )
            await interaction.response.send_message(status_message)
        except Exception as e:
            error_message = (
                f"There was an issue checking the bot's status. "
                f"Please contact the creator (Ogthem) for assistance.\n"
                f"Error: {e}"
            )
            await interaction.response.send_message(error_message)

async def setup(bot):
    cog = Status(bot)
    await bot.add_cog(cog)
    await cog.cog_load()
