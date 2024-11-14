import requests
import discord
from discord.ext import commands
from discord import app_commands

class SpotifyDownloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="spotify", description="Search for and download a song from Spotify.")
    async def spotify(self, interaction: discord.Interaction, spotify_url: str):
        await interaction.response.send_message("Processing your request...", ephemeral=True)

        try:
            # Prepare the request to search the song
            api_url = "https://spotify23.p.rapidapi.com/search/"
            querystring = {
                "q": spotify_url,
                "type": "multi",
                "offset": "0",
                "limit": "10",
                "numberOfTopResults": "5"
            }
            headers = {
                "x-rapidapi-key": "5e6976078bmsheb89f5f8d17f7d4p1b5895jsnb31e587ad8cc",
                "x-rapidapi-host": "spotify23.p.rapidapi.com"
            }

            # Send the request to the API
            response = requests.get(api_url, headers=headers, params=querystring)

            # Check if the response was successful
            response_data = response.json()

            if response.status_code != 200 or not response_data.get('tracks') or not response_data['tracks'].get('items'):
                await interaction.followup.send("Failed to find the song. Please check the Spotify URL and try again.", ephemeral=True)
                return

            # Get the first track result
            track = response_data['tracks']['items'][0]
            track_name = track['name']
            track_artist = ", ".join(artist['name'] for artist in track['artists'])
            track_url = track['external_urls']['spotify']

            # Send track details and link to the user
            await interaction.followup.send(f"Here is the track you requested:\n"
                                            f"**{track_name}** by **{track_artist}**\n"
                                            f"Listen on Spotify: [Click here]({track_url})", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SpotifyDownloader(bot))
