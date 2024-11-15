import discord
from discord.ext import commands
from pytube import YouTube
import os

class YouTubeMP4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="youtubemp4", description="Download a YouTube video in MP4 format.")
    async def youtubemp4(self, ctx, url: str):
        try:
            await ctx.defer()  # Defer response for longer processing time

            # Download video
            yt = YouTube(url)
            video = yt.streams.filter(file_extension="mp4", res="360p").first()  # You can choose resolution
            if video is None:
                await ctx.send("No MP4 video available at 360p resolution. Please try a different video or resolution.")
                return

            # Define download path and file name
            file_path = video.download(filename="video.mp4")
            await ctx.send("Download successful! Uploading...")

            # Send file to Discord
            await ctx.send(file=discord.File(file_path))

            # Clean up file after sending
            os.remove(file_path)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

# Add the cog to the bot
def setup(bot):
    bot.add_cog(YouTubeMP4(bot))
