import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import os

class YouTubeMP3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="youtube_mp3", description="Convert a YouTube video to MP3 and get the file.")
    async def youtube_mp3(self, interaction: discord.Interaction, url: str):
        await interaction.response.send_message("Processing your request...", ephemeral=True)

        try:
            # Ensure the downloads folder exists
            if not os.path.exists("downloads"):
                os.makedirs("downloads")

            # yt-dlp options to extract audio only in MP3 format
            ydl_opts = {
                'format': 'bestaudio/best',  # Download only the best quality audio
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_id = info_dict.get("id", None)
                audio_file = f"downloads/{video_id}.mp3"

            # Send the MP3 file to the user
            await interaction.followup.send("Here is your MP3 file:", file=discord.File(audio_file))

            # Clean up the MP3 file after sending
            os.remove(audio_file)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(YouTubeMP3(bot))
