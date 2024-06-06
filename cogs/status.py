import discord
from discord.ext import commands

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="status", description="Check the bot's status")
    async def status(self, ctx: discord.ApplicationContext):
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
            await ctx.respond(status_message)
        except Exception as e:
            error_message = (
                f"There was an issue checking the bot's status. "
                f"Please contact the creator (Ogthem) for assistance.\n"
                f"Error: {e}"
            )
            await ctx.respond(error_message)

async def setup(bot):
    await bot.add_cog(Status(bot))
