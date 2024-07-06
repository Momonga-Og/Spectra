import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image
import os

# Ensure the temp directory exists
if not os.path.exists("temp"):
    os.makedirs("temp")

# Allowed formats
FORMATS = ["JPEG", "JPG", "PNG", "WEBP", "BMP"]

class ImageConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="image_converter", description="Convert an image to different formats (JPEG, JPG, PNG, WEBP, BMP).")
    async def image_converter(self, interaction: discord.Interaction, attachment: discord.Attachment):
        await interaction.response.send_message("Please select the format you want to convert to:", ephemeral=True)

        # Create a select menu for formats
        class FormatSelect(discord.ui.Select):
            def __init__(self):
                options = [discord.SelectOption(label=format) for format in FORMATS]
                super().__init__(placeholder="Choose an image format...", min_values=1, max_values=1, options=options)

            async def callback(self, select_interaction: discord.Interaction):
                format = self.values[0]
                await select_interaction.response.send_message("Processing your image...", ephemeral=True)
                
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
                    await select_interaction.followup.send("Here is your converted image:", file=discord.File(output_path))

                    # Clean up the files
                    os.remove(file_path)
                    os.remove(output_path)

                except Exception as e:
                    await select_interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

        view = discord.ui.View()
        view.add_item(FormatSelect())
        await interaction.followup.send(view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ImageConverter(bot))
