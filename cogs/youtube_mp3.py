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
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'cookiefile': 'extra/youtube_cookies.txt',
                'sleep_interval_requests': 2,
                'throttled_rate': '100K',
                'noplaylist': True,
                'extractor_args': {
                    'youtube': {
                        'player_skip': ['configs', 'config', 'js'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.5',
                },
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
