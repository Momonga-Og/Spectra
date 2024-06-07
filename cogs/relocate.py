import discord
from discord.ext import commands
from discord import app_commands
import logging

class Relocate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="relocate", description="Relocate a message to a specified channel")
    async def relocate(self, interaction: discord.Interaction, message_id: str, target_channel: discord.TextChannel):
        # Fetch the message
        try:
            message = await interaction.channel.fetch_message(int(message_id))
        except discord.NotFound:
            await interaction.response.send_message("Message not found.")
            return
        except discord.HTTPException as e:
            logging.exception(f"HTTPException: {e}")
            await interaction.response.send_message("Failed to fetch the message.")
            return

        # Check if the message has content or attachments
        if not message.content and not message.attachments:
            await interaction.response.send_message("The message has no content or attachments to relocate.")
            return

        # Repost the message content and attachments
        files = [await attachment.to_file() for attachment in message.attachments]
        await target_channel.send(content=message.content, files=files)
        
        # Optionally delete the original message
        await message.delete()

        # Send confirmation to the user
        await interaction.response.send_message(f"Message relocated to {target_channel.mention}")

async def setup(bot):
    cog = Relocate(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('relocate'):
        bot.tree.add_command(cog.relocate)
