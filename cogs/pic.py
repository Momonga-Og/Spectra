import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import logging

logger = logging.getLogger(__name__)

class Pic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @app_commands.command(name="genpic", description="Generate an image using Picogen")
    async def genpic(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        try:
            async with self.session.get(f'https://api.picogen.ai/generate?prompt={prompt}') as response:
                if response.status == 200:
                    data = await response.json()
                    image_url = data.get('image_url')
                    if image_url:
                        await interaction.followup.send(image_url)
                    else:
                        await interaction.followup.send("No image generated.")
                else:
                    await interaction.followup.send(f"Failed to generate image. Status code: {response.status}")
        except Exception as e:
            logger.exception("Error generating image")
            await interaction.followup.send("An error occurred while generating the image.")

async def setup(bot):
    await bot.add_cog(Pic(bot))
