import discord
from discord.ext import commands
from discord import app_commands
import os

class Save(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="replace_file", description="Replace the file in a user's message while keeping the message content.")
    async def replace_file(self, interaction: discord.Interaction, message_id: str, new_file: discord.Attachment):
        """
        Replaces a file in a user's message by removing the old file and sending a new one while keeping the message content.
        
        Args:
            interaction (discord.Interaction): The slash command interaction.
            message_id (str): The ID of the message to modify.
            new_file (discord.Attachment): The new file to replace the old one.
        """
        # Defer the interaction
        await interaction.response.defer()

        try:
            # Fetch the channel and the message
            channel = interaction.channel
            message = await channel.fetch_message(int(message_id))
            if not message:
                await interaction.followup.send("Message not found.", ephemeral=True)
                return

            # Check if the message has attachments
            if not message.attachments:
                await interaction.followup.send("The message does not contain any files to replace.", ephemeral=True)
                return

            # Download the new file
            file_path = f"./{new_file.filename}"
            await new_file.save(file_path)

            # Edit the message: Keep the content but inform about the file replacement
            await message.edit(content=f"{message.content}\n\n*(Attachment has been replaced)*")

            # Send the new file in the same context
            with open(file_path, "rb") as file:
                await channel.send(content=f"Updated file for the message: [Jump to message]({message.jump_url})", 
                                   file=discord.File(file, filename=new_file.filename))

            # Clean up the temporary file
            os.remove(file_path)

            await interaction.followup.send("File replaced successfully!", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Save(bot))
