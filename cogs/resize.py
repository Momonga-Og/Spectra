import discord
from discord.ext import commands
from discord import app_commands
import moviepy.editor as mp
import os

class ResizeVideo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="resize", description="Resize a video to YouTube Shorts format (1080x1920, 9:16).")
    async def resize(self, interaction: discord.Interaction, attachment: discord.Attachment):
        await interaction.response.defer(ephemeral=True)

        try:
            # Download the video
            file_path = f"temp/{attachment.filename}"
            await attachment.save(file_path)

            # Resize the video
            video = mp.VideoFileClip(file_path)
            video_resized = video.resize(height=1920).resize(width=1080)
            
            output_path = file_path.rsplit('.', 1)[0] + "_resized.mp4"
            video_resized.write_videofile(output_path)

            # Send the resized video to the user
            await interaction.followup.send("Here is your resized video:", file=discord.File(output_path))

            # Clean up the files
            os.remove(file_path)
            os.remove(output_path)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ResizeVideo(bot))
