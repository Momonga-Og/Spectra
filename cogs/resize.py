import discord
from discord.ext import commands
from discord import app_commands
import moviepy.editor as mp
import asyncio
import os

class ResizeVideo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="resize", description="Resize a video to YouTube Shorts format (1080x1920, 9:16).")
    async def resize(self, interaction: discord.Interaction, attachment: discord.Attachment):
        await interaction.response.defer(ephemeral=True)
        
        # Create the temp directory if it doesn't exist
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        try:
            # Download the video
            file_path = f"temp/{attachment.filename}"
            await attachment.save(file_path)

            # Run the video processing in a separate thread to avoid blocking the main thread
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.process_video, file_path, interaction)
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

    def process_video(self, file_path, interaction):
        try:
            # Resize the video
            video = mp.VideoFileClip(file_path)
            video_resized = video.resize(height=1920).resize(width=1080)
            output_path = file_path.rsplit('.', 1)[0] + "_resized.mp4"
            video_resized.write_videofile(output_path)

            # Send the resized video to the user
            loop = asyncio.get_event_loop()
            loop.create_task(self.send_video(interaction, output_path))

            # Clean up the files
            os.remove(file_path)
            os.remove(output_path)

        except Exception as e:
            loop = asyncio.get_event_loop()
            loop.create_task(interaction.followup.send(f"An error occurred: {e}", ephemeral=True))

    async def send_video(self, interaction, output_path):
        await interaction.followup.send("Here is your resized video:", file=discord.File(output_path))

async def setup(bot):
    await bot.add_cog(ResizeVideo(bot))
