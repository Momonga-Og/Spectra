import discord
from discord.ext import commands
from discord import app_commands

class ClearMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Delete a specified number of messages in this channel (1-50).")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, count: int):
        if count < 1 or count > 50:
            await interaction.response.send_message("You can only delete between 1 and 50 messages.", ephemeral=True)
            return

        # Defer the interaction response to avoid timeouts during message deletion
        await interaction.response.defer(ephemeral=True)

        try:
            deleted = await interaction.channel.purge(limit=count + 1)  # +1 to include the command message
            await interaction.followup.send(f"Deleted {len(deleted) - 1} messages.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I do not have permission to delete messages in this channel.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"Failed to delete messages: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearMessages(bot))
