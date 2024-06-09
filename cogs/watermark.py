import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import logging
import os

class Watermark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def add_watermark(self, image_bytes, user_name, server_name):
        with Image.open(image_bytes) as im:
            draw = ImageDraw.Draw(im)
            font = ImageFont.load_default()
            text = f"{user_name} - {server_name}"
            textwidth, textheight = draw.textsize(text, font)
            
            # Calculate position for the text
            width, height = im.size
            x = width - textwidth - 10
            y = height - textheight - 10
            
            # Draw the text on the image
            draw.text((x, y), text, font=font)
            
            # Save the image with watermark
            output_path = f"watermarked_{user_name}.png"
            im.save(output_path)
            
        return output_path

    @app_commands.command(name="watermark", description="Watermark an image with your username and the server name")
    async def watermark(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer(ephemeral=True)
        try:
            user_name = interaction.user.name
            server_name = interaction.guild.name
            async with aiohttp.ClientSession() as session:
                async with session.get(image.url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        image_path = await self.add_watermark(image_bytes, user_name, server_name)
                        await interaction.followup.send(file=discord.File(image_path))
                        os.remove(image_path)
                    else:
                        await interaction.followup.send("Failed to download the image.")
        except Exception as e:
            logging.exception(f"Error in watermark command: {e}")
            await interaction.followup.send(f"An error occurred: {e}")

    @app_commands.command(name="watermark-user", description="Watermark an image with another user's name and the server name")
    async def watermark_user(self, interaction: discord.Interaction, image: discord.Attachment, user: discord.Member):
        await interaction.response.defer(ephemeral=True)
        try:
            user_name = user.name
            server_name = interaction.guild.name
            async with aiohttp.ClientSession() as session:
                async with session.get(image.url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        image_path = await self.add_watermark(image_bytes, user_name, server_name)
                        await interaction.followup.send(file=discord.File(image_path))
                        os.remove(image_path)
                    else:
                        await interaction.followup.send("Failed to download the image.")
        except Exception as e:
            logging.exception(f"Error in watermark-user command: {e}")
            await interaction.followup.send(f"An error occurred: {e}")

async def setup(bot):
    cog = Watermark(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('watermark'):
        bot.tree.add_command(cog.watermark)
    if not bot.tree.get_command('watermark-user'):
        bot.tree.add_command(cog.watermark_user)
