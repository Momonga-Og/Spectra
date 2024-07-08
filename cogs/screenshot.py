import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import io

class Screenshot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="screen-shot", description="Take a screenshot of the current channel's recent messages.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def screen_shot(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Fetch recent messages
        messages = []
        async for message in interaction.channel.history(limit=20):
            messages.append(message)

        # Reverse to show messages from oldest to newest
        messages.reverse()

        # Create an image
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        y_text = 20
        for message in messages:
            text = f"{message.author.display_name}: {message.content}"
            d.text((20, y_text), text, fill=(0, 0, 0), font=font)
            y_text += 20

        # Save the image to a BytesIO object
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.followup.send("Here is the screenshot of the recent messages:", file=discord.File(fp=image_binary, filename='screenshot.png'))

async def setup(bot):
    await bot.add_cog(Screenshot(bot))
