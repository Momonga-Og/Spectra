import requests
import discord
from discord.ext import commands
from discord import app_commands

class YouTubeMP3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="youtube_mp3", description="Convert a YouTube video to MP3 and get the file.")
    async def youtube_mp3(self, interaction: discord.Interaction, url: str):
        await interaction.response.send_message("Processing your request...", ephemeral=True)

        try:
            # Extract the video ID from the URL
            video_id = url.split('v=')[-1] if 'v=' in url else url.split('/')[-1]
            
            # Prepare the request
            api_url = "https://youtube-mp36.p.rapidapi.com/dl"
            querystring = {"id": video_id}
            headers = {
                "x-rapidapi-key": "5e6976078bmsheb89f5f8d17f7d4p1b5895jsnb31e587ad8cc",
                "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
            }

            # Send the request to the API
            response = requests.get(api_url, headers=headers, params=querystring)

            # Check the response from the API
            response_data = response.json()

            if response.status_code != 200 or not response_data.get('link'):
                await interaction.followup.send("Failed to convert the video. Please check the URL and try again.", ephemeral=True)
                return

            # Get the MP3 download link
            mp3_url = response_data['link']

            # Send the MP3 download link to the user
            await interaction.followup.send(f"Here is your MP3 file: [Download MP3]({mp3_url})", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(YouTubeMP3(bot))
