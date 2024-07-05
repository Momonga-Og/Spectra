import discord
from discord.ext import commands
from pytube import YouTube
from moviepy.editor import *
import os

class YouTubeMP3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="youtube-mp3", help="Convert a YouTube video to MP3 and get the file.")
    async def youtube_mp3(self, ctx, url: str):
        await ctx.send("Processing your request...")

        try:
            # Download the YouTube video
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            download_path = audio_stream.download()

            # Convert to MP3
            output_path = download_path.replace(".mp4", ".mp3")
            audio_clip = AudioFileClip(download_path)
            audio_clip.write_audiofile(output_path)
            audio_clip.close()

            # Remove the original file
            os.remove(download_path)

            # Send the MP3 file to the user
            await ctx.send("Here is your MP3 file:", file=discord.File(output_path))

            # Clean up the MP3 file after sending
            os.remove(output_path)

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(YouTubeMP3(bot))
