import discord
from discord import app_commands
from discord.ext import commands

class GuildCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="guild", description="Create a new guild with a specified name.")
    async def create_guild(self, interaction: discord.Interaction, name: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
        
        try:
            # Attempt to create a new guild
            new_guild = await self.bot.create_guild(name=name)
            
            # Create default channels (like a general text channel)
            general_channel = await new_guild.create_text_channel("general")
            await general_channel.send(f"Welcome to {name}!")

            await interaction.response.send_message(f"New guild '{new_guild.name}' created successfully!", ephemeral=True)

        except discord.errors.HTTPException as e:
            if e.code == 30001:
                await interaction.response.send_message("Failed to create guild: Maximum number of guilds reached, or bot permissions issue.", ephemeral=True)
            else:
                await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GuildCreator(bot))
