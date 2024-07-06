import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image
import os

class ImageConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="image_converter", description="Convert an image to different formats (JPEG, JPG, PNG, WEBP, BMP).")
    async def image_converter(self, interaction: discord.Interaction, format: str, attachment: discord.Attachment):
        await interaction.response.send_message("Processing your image...", ephemeral=True)

        # Allowed formats
        formats = ["JPEG", "JPG", "PNG", "WEBP", "BMP"]

        if format.upper() not in formats:
            await interaction.followup.send("Unsupported format. Please choose from JPEG, JPG, PNG, WEBP, BMP.", ephemeral=True)
            return

        try:
            # Download the image
            file_path = f"temp/{attachment.filename}"
            await attachment.save(file_path)

            # Open the image
            img = Image.open(file_path)

            # Determine output path
            output_path = file_path.rsplit('.', 1)[0] + f".{format.lower()}"

            # Save the image in the desired format
            img.save(output_path, format.upper())

            # Send the converted image to the user
            await interaction.followup.send("Here is your converted image:", file=discord.File(output_path))

            # Clean up the files
            os.remove(file_path)
            os.remove(output_path)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ImageConverter(bot))

