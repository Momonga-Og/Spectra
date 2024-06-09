import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import logging

class Watermark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="watermark", description="Watermark an image with your username, server name, and profile picture")
    async def watermark(self, interaction: discord.Interaction, image: discord.Attachment):
        try:
            # Ensure the attachment is an image
            if not image.content_type.startswith('image/'):
                await interaction.response.send_message("Please upload a valid image.")
                return

            async with aiohttp.ClientSession() as session:
                # Download the user's profile picture
                profile_image_url = interaction.user.display_avatar.url
                async with session.get(profile_image_url) as response:
                    profile_image_data = await response.read()

            profile_image = Image.open(io.BytesIO(profile_image_data)).convert("RGBA")
            profile_image = profile_image.resize((50, 50))  # Resize profile picture

            # Download the image to be watermarked
            image_data = await image.read()
            with Image.open(io.BytesIO(image_data)).convert("RGBA") as img:
                draw = ImageDraw.Draw(img)
                # Use a TTF font and increase size; ensure the path to the font is correct
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                font = ImageFont.truetype(font_path, 30)
                
                # Watermark text
                watermark_text = f"{interaction.user.name} - {interaction.guild.name}"

                # Position for the watermark text
                text_position = (10, img.height - 60)
                
                # Apply the watermark text
                draw.text(text_position, watermark_text, font=font, fill=(255, 255, 255, 128))  # White text with transparency

                # Position for the profile picture
                profile_position = (10, img.height - 110)
                
                # Paste the profile picture onto the image
                img.paste(profile_image, profile_position, profile_image)

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
