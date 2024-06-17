import discord
from discord.ext import commands
from discord import app_commands

class WriteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="write", description="Send an anonymous message. Only admins can use this command.")
    async def write(self, interaction: discord.Interaction, message: str):
        # Check if the user is an admin
        if interaction.user.guild_permissions.administrator:
            # Send the anonymized message
            await interaction.response.send_message(f"Anonymous Message: {message}", ephemeral=False)
        else:
            await interaction.response.send_message("You do not have the necessary permissions to use this command.", ephemeral=True)

    @write.error
    async def write_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You do not have the necessary permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(WriteCog(bot).write)
