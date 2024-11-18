import discord
from discord import app_commands
from discord.ext import commands
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import re
import cv2
from fuzzywuzzy import fuzz

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
            img, thresh = self.preprocess_image(file_path)
            extracted_text = pytesseract.image_to_string(img, lang='fra')  # Perform OCR

            # Extract required information using regex and fuzzy matching
            location = self.extract_location(extracted_text)
            guild = self.extract_guild(extracted_text)
            alliance = self.extract_alliance(extracted_text)

            # Handle missing data feedback
            missing_info = []
            if location == "Not found": missing_info.append("location")
            if guild == "Not found": missing_info.append("guild")
            if alliance == "Not found": missing_info.append("alliance")

            # Prepare the response message
            response = (
                f"**Extracted Information:**\n"
                f"**Location:** {location}\n"
                f"**Guild:** {guild}\n"
                f"**Alliance:** {alliance}\n"
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
        # Open and preprocess the image for OCR
        img = Image.open(file_path)
        img = img.convert('L')  # Convert to grayscale
        img = img.filter(ImageFilter.MedianFilter())  # Median filter for noise reduction
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)  # Enhance the contrast

        # Convert to OpenCV format for additional thresholding
        img_cv = cv2.imread(file_path)  # Convert to OpenCV format
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        return img, thresh

    def extract_location(self, text):
        # Use regex to extract location (assume a pattern like "Location: [Some Location]")
        location_match = re.search(r"location\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
        if location_match:
            return location_match.group(1).strip()
        return "Not found"

    def extract_guild(self, text):
        # Use fuzzy matching to find the guild name
        guild_match = re.search(r"guild\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
        if guild_match:
            guild_name = guild_match.group(1).strip()
            # Example of known guild names for fuzzy matching
            known_guilds = ["GuildA", "GuildB", "GuildC"]  # Customize this list
            best_match = max(known_guilds, key=lambda x: fuzz.partial_ratio(guild_name, x))
            if fuzz.partial_ratio(guild_name, best_match) > 80:  # 80% match threshold
                return best_match
            return guild_name
        return "Not found"

    def extract_alliance(self, text):
        # Use regex to extract alliance (assume a pattern like "Alliance: [Some Alliance]")
        alliance_match = re.search(r"alliance\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
        if alliance_match:
            return alliance_match.group(1).strip()
        return "Not found"

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(PercoPos(bot))
