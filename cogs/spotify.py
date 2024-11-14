import requests
import discord
from discord.ext import commands
from discord import app_commands

class SpotifyDownloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="spotify", description="Download music, EPs, or albums from Spotify.")
    async def spotify(self, interaction: discord.Interaction, spotify_url: str):
        await interaction.response.send_message("Processing your request...", ephemeral=True)

        try:
            # Prepare the request to download the song
            api_url = "https://spotify-downloader9.p.rapidapi.com/downloadSong"
            querystring = {"songId": spotify_url}
            headers = {
                "x-rapidapi-key": "5e6976078bmsheb89f5f8d17f7d4p1b5895jsnb31e587ad8cc",
                "x-rapidapi-host": "spotify-downloader9.p.rapidapi.com"
            }

            # Send the request to the API
            response = requests.get(api_url, headers=headers, params=querystring)

            # Check the response from the API
            response_data = response.json()

            if response.status_code != 200 or not response_data.get('url'):
                await interaction.followup.send("Failed to download the song. Please check the Spotify URL and try again.", ephemeral=True)
                return

            # Get the MP3 download link
            mp3_url = response_data['url']

            # Send the MP3 download link to the user
            await interaction.followup.send(f"Here is your MP3 file: [Download MP3]({mp3_url})", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SpotifyDownloader(bot))
