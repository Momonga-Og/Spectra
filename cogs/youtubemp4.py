import discord
from discord import app_commands
from discord.ext import commands
from pytube import YouTube
import os

class YouTubeMP4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Use @app_commands.command for the slash command
    @app_commands.command(name="youtubemp4", description="Download a YouTube video in MP4 format.")
    async def youtubemp4(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()  # Defer response for processing time

        try:
            # Download video
            yt = YouTube(url)
            video = yt.streams.filter(file_extension="mp4", res="360p").first()  # Choose resolution here
            if video is None:
                await interaction.followup.send("No MP4 video available at 360p resolution. Try another video or resolution.")
                return

            # Define download path and file name
            file_path = video.download(filename="video.mp4")
            await interaction.followup.send("Download successful! Uploading...")

            # Send file to Discord
            await interaction.followup.send(file=discord.File(file_path))

            # Clean up file after sending
            os.remove(file_path)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")

# Add the Cog to the bot
async def setup(bot):
    await bot.add_cog(YouTubeMP4(bot))
