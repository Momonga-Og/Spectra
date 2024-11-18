import discord
from discord.ext import commands
import pytesseract
from PIL import Image
import os
import re

class PercoPos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="percopos")
    async def percopos(self, ctx):
        if not ctx.message.attachments:
            await ctx.send("Please upload an image file with the command!")
            return

        # Download the uploaded image
        attachment = ctx.message.attachments[0]
        file_extension = attachment.filename.split(".")[-1].lower()
        supported_extensions = ["jpg", "jpeg", "jfif", "pjpeg", "pjp", "png"]
        
        if file_extension not in supported_extensions:
            await ctx.send("Unsupported file format. Please upload a valid image file!")
            return

        file_path = f"./temp_image.{file_extension}"
        await attachment.save(file_path)

        try:
            # Perform OCR on the image
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang="eng")
            
            # Extract information
            location = self.extract_location(text)
            guild = self.extract_guild(text)
            alliance = self.extract_alliance(text)
            kamas = self.extract_kamas(text)
            
            # Prepare the response
            response = (
                f"**Extracted Information:**\n"
                f"**Location:** {location}\n"
                f"**Guild:** {guild}\n"
                f"**Alliance:** {alliance}\n"
                f"**Kamas:** {kamas}\n"
            )
            await ctx.send(response)
        
        except Exception as e:
            await ctx.send(f"An error occurred while processing the image: {e}")
        finally:
            # Clean up by deleting the image file
            if os.path.exists(file_path):
                os.remove(file_path)

    def extract_location(self, text):
        # Find coordinates in the format "-2 : -28"
        match = re.search(r"-\d+\s?:\s?-?\d+", text)
        return match.group() if match else "Not found"

    def extract_guild(self, text):
        # Look for "guilde <name>"
        match = text.split("\n")
        for line in match:
            if "guilde" in line.lower():
                return line.split("guilde")[1].strip()
        return "Not found"

    def extract_alliance(self, text):
        # Look for "abréviation <abbr>"
        if "abréviation" in text.lower():
            return text.split("abréviation")[1].strip()
        return "Not found"

    def extract_kamas(self, text):
        # Look for "Kamas"
        match = re.search(r"\d+\s?Kamas", text)
        return match.group() if match else "Not found"

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(PercoPos(bot))
