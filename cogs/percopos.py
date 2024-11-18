import discord
from discord import app_commands
from discord.ext import commands
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import re

class PercoPos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="percopos", description="Upload an image to extract Perceptor details")
    @app_commands.describe(image="The image containing the Perceptor details")
    async def percopos(self, interaction: discord.Interaction, image: discord.Attachment):
        # Validate file type
        file_extension = image.filename.split(".")[-1].lower()
        supported_extensions = ["jpg", "jpeg", "jfif", "pjpeg", "pjp", "png"]
        
        if file_extension not in supported_extensions:
            await interaction.response.send_message(
                "Unsupported file format. Please upload a valid image file!", ephemeral=True
            )
            return

        # Save the uploaded file
        file_path = f"./temp_image.{file_extension}"
        await image.save(file_path)

        try:
            # Preprocess and perform OCR on the image
            img = self.preprocess_image(file_path)
            text = pytesseract.image_to_string(img, lang="eng")

            # Extract required information
            location = self.extract_location(text)
            guild = self.extract_guild(text)
            alliance = self.extract_alliance(text)
            kamas = self.extract_kamas(text)

            # Handle missing data feedback
            missing_info = []
            if location == "Not found": missing_info.append("location")
            if guild == "Not found": missing_info.append("guild")
            if alliance == "Not found": missing_info.append("alliance")
            if kamas == "Not found": missing_info.append("kamas")

            # Prepare the response
            response = (
                f"**Extracted Information:**\n"
                f"**Location:** {location}\n"
                f"**Guild:** {guild}\n"
                f"**Alliance:** {alliance}\n"
                f"**Kamas:** {kamas}\n"
            )
            if missing_info:
                response += f"\n⚠️ **Could not extract:** {', '.join(missing_info)}. Please ensure the image is clear."

            await interaction.response.send_message(response)

        except Exception as e:
            await interaction.response.send_message(f"An error occurred while processing the image: {e}")
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

    def preprocess_image(self, file_path):
        """Preprocess the image to improve OCR results."""
        img = Image.open(file_path)
        img = img.convert("L")  # Convert to grayscale
        img = img.filter(ImageFilter.MedianFilter())  # Reduce noise
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)  # Increase contrast
        return img

    def extract_location(self, text):
        """Extract coordinates in the format -2 : -28 or similar."""
        match = re.search(r"-?\d+\s?:\s?-?\d+", text)
        return match.group() if match else "Not found"

    def extract_guild(self, text):
        """Extract the guild name."""
        lines = text.split("\n")
        for line in lines:
            if "guilde" in line.lower():
                match = re.search(r"guilde\s*[:\-]?\s*(.*)", line, re.IGNORECASE)
                return match.group(1).strip() if match else "Not found"
        return "Not found"

    def extract_alliance(self, text):
        """Extract the alliance abbreviation."""
        lines = text.split("\n")
        for line in lines:
            if "abréviation" in line.lower():
                match = re.search(r"abréviation\s*[:\-]?\s*(.*)", line, re.IGNORECASE)
                return match.group(1).strip() if match else "Not found"
        return "Not found"

    def extract_kamas(self, text):
        """Extract the amount of Kamas."""
        match = re.search(r"(\d[\d\s]*\s?Kamas)", text, re.IGNORECASE)
        if match:
            return match.group(1).replace(" ", "").strip()
        return "Not found"

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(PercoPos(bot))
