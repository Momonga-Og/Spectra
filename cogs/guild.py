import discord
from discord import app_commands
from discord.ext import commands

class GuildCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="guild", description="Create a new guild with a specified name.")
    async def create_guild(self, interaction: discord.Interaction, name: str):
        # Check if the user has the necessary permissions, adjust as needed
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return

        # Create the guild
        try:
            new_guild = await self.bot.create_guild(name=name)
            await interaction.response.send_message(f"New guild '{new_guild.name}' created successfully!", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Failed to create guild: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GuildCreator(bot))
