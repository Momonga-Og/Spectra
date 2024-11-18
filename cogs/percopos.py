import discord
from discord import app_commands
from discord.ext import commands
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import re
import cv2

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
            text = pytesseract.image_to_string(img, lang='fra')  # Specify language

            # Extract required information
            location = self.extract_location(thresh)
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
        img = Image.open(file_path)
        img = img.convert('L')
        img = img.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)

        # Additional preprocessing for location extraction
        img_cv = cv2.imread(file_path)  # Convert to OpenCV format
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        return img, thresh

    def extract_location(self, img_thresh):
        contours, _ = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h > w * 2:  # Filter for location box aspect ratio
                location_roi = img_thresh[y:y+h, x:x+w]
                location_text = pytesseract.image_to_string(location_roi, lang='fra')
                return location_text.strip()
        return "Not found"

    def extract_guild(self, text):
        # Improved regular expression with language-specific keywords
        guild_match = re.search(r"guilde\s*:\s*(.*)", text, re.IGNORECASE)
        if guild_match:
            return guild_match.group(1).strip()
        return "Not found"

    def extract_alliance(self, text):
        alliance_match = re.search(r"alliance\s*:\s*(.*)", text, re.IGNORECASE)
        if alliance_match:
            return alliance_match.group(1).strip()
        return "Not found"

    def extract_kamas(self, text):
        kamas_match = re.search(r"(\d+\s*Kamas)", text, re.IGNORECASE)
        if kamas_match:
            return kamas_match.group(1).strip()
        return "Not found"

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(PercoPos(bot))
