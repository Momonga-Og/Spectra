import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import io
import logging

class Watermark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="watermark", description="Watermark an image with your username and server name")
    async def watermark(self, interaction: discord.Interaction, image: discord.Attachment):
        try:
            # Ensure the attachment is an image
            if not image.content_type.startswith('image/'):
                await interaction.response.send_message("Please upload a valid image.")
                return

            # Download the image
            image_data = await image.read()
            with Image.open(io.BytesIO(image_data)) as img:
                draw = ImageDraw.Draw(img)
                font = ImageFont.load_default()  # Default font, can be replaced with a specific TTF font

                # Watermark text
                watermark_text = f"{interaction.user.name} - {interaction.guild.name}"
                
                # Get the image dimensions
                width, height = img.size
                text_width, text_height = draw.textsize(watermark_text, font=font)
                
                # Position the watermark at the bottom right corner
                position = (width - text_width - 10, height - text_height - 10)
                
                # Apply the watermark
                draw.text(position, watermark_text, font=font, fill=(255, 255, 255, 128))  # White text with transparency

                # Save the watermarked image to a bytes object
                output_buffer = io.BytesIO()
                img.save(output_buffer, format="PNG")
                output_buffer.seek(0)

                # Send the watermarked image
                file = discord.File(fp=output_buffer, filename="watermarked.png")
                await interaction.response.send_message("Here is your watermarked image:", file=file)

        except Exception as e:
            logging.exception(f"Error in watermark command: {e}")
            await interaction.response.send_message("An error occurred while processing your image.")

async def setup(bot):
    cog = Watermark(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('watermark'):
        bot.tree.add_command(cog.watermark)
