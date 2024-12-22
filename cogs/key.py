import discord
from discord import app_commands
from discord.ext import commands
from database import get_all_voice_activity

class KeyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="key", description="Export voice activity data")
    async def key(self, interaction: discord.Interaction):
        # Check if the user is the bot creator
        if interaction.user.id != 486652069831376943:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        # Ensure the command is invoked in DMs only
        if interaction.guild is not None:
            await interaction.response.send_message(
                "This command can only be used in DMs.", ephemeral=True
            )
            return

        # Fetch data and write to a text file
        data = get_all_voice_activity()
        output_file = "voice_activity.txt"
        
        with open(output_file, "w") as file:
            for row in data:
                file.write(f"{row}\n")
        
        await interaction.response.send_message(
            "Here is the voice activity data:", file=discord.File(output_file)
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(KeyCommand(bot))
