import discord
from discord import app_commands
from discord.ext import commands
from pytube import YouTube
import os

class YouTubeMP4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="youtubemp4", description="Download a YouTube video in MP4 format.")
    async def youtubemp4(self, interaction: discord.Interaction, url: str):
        try:
            # Direct response without defer
            await interaction.response.defer(thinking=True)

            # Download the video
            yt = YouTube(url)
            video = yt.streams.filter(file_extension="mp4", res="360p").first()
            if video is None:
                await interaction.followup.send("No MP4 video available at 360p resolution. Try another video or resolution.")
                return

            # Define download path and file name
            file_path = video.download(filename="video.mp4")

            # Check file size (Discord's 8 MB limit for non-Nitro users)
            file_size = os.path.getsize(file_path)
            if file_size > 8 * 1024 * 1024:  # 8 MB
                await interaction.followup.send("The video is too large to upload to Discord. Try a shorter video.")
                os.remove(file_path)  # Clean up
                return

            # Send file to Discord
            await interaction.followup.send(file=discord.File(file_path))

            # Clean up file after sending
            os.remove(file_path)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(YouTubeMP4(bot))
