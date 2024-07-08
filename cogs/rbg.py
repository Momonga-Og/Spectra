import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image
import io
from rembg import remove

class RemoveBackground(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rbg", description="Remove the background from an uploaded image.")
    async def rbg(self, interaction: discord.Interaction, attachment: discord.Attachment):
        await interaction.response.defer(ephemeral=True)

        try:
            # Download the image
            file_path = f"temp/{attachment.filename}"
            await attachment.save(file_path)

            # Open the image
            with open(file_path, 'rb') as input_file:
                input_image = input_file.read()
                output_image = remove(input_image)

            # Save the processed image to a BytesIO object
            output_file = io.BytesIO(output_image)
            output_file.seek(0)

            # Send the processed image to the user
            await interaction.followup.send("Here is your image with the background removed:", file=discord.File(fp=output_file, filename=f"no_bg_{attachment.filename}"))

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RemoveBackground(bot))
