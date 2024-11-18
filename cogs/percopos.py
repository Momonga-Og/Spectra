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
            text_regions = self.extract_text_by_region(file_path, lang='fra')  # Use dynamic text regions

            # Extract information dynamically from text regions
            location, guild, alliance = "Not found", "Not found", "Not found"

            for region in text_regions:
                # Example: Check if the region contains 'location' or 'guild'
                if 'location' in region['text'].lower():
                    location = self.extract_location_from_region(region)
                elif 'guild' in region['text'].lower():
                    guild = self.extract_guild_from_region(region)
                elif 'alliance' in region['text'].lower():
                    alliance = self.extract_alliance_from_region(region)

            # Handle missing data feedback
            missing_info = []
            if location == "Not found": missing_info.append("location")
            if guild == "Not found": missing_info.append("guild")
            if alliance == "Not found": missing_info.append("alliance")

            # Prepare the response
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

        # Convert to OpenCV format for thresholding
        img_cv = cv2.imread(file_path)  # Convert to OpenCV format
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        return img, thresh

    def extract_text_by_region(self, file_path, lang='fra'):
        # Perform layout analysis using Tesseract OCR
        custom_config = r'--oem 3 --psm 6'  # PSM 6 is good for blocks of text
        img = Image.open(file_path)
        
        # Extract bounding boxes for each text block
        details = pytesseract.image_to_boxes(img, lang=lang, config=custom_config)
        text_regions = []

        for detail in details.splitlines():
            b = detail.split()
            text_regions.append({
                "text": b[0],
                "x1": int(b[1]),
                "y1": int(b[2]),
                "x2": int(b[3]),
                "y2": int(b[4])
            })

        return text_regions

    def extract_location_from_region(self, region):
        # Extract location from a specific text region
        return region['text'].strip()

    def extract_guild_from_region(self, region):
        # Fuzzy match to extract the guild name more accurately
        guild_name = region['text'].strip()
        possible_guilds = ["GuildA", "GuildB", "GuildC"]  # Example guild list

        # Use fuzzy matching to find the closest match
        best_match = max(possible_guilds, key=lambda x: fuzz.partial_ratio(guild_name, x))
        if fuzz.partial_ratio(guild_name, best_match) > 80:  # Set a threshold for fuzzy matching
            return best_match
        return guild_name

    def extract_alliance_from_region(self, region):
        # Extract alliance name from the region
        alliance_name = region['text'].strip()
        return alliance_name

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(PercoPos(bot))
