import http.client
import json
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
            # Set up connection to RapidAPI
            conn = http.client.HTTPSConnection("youtube-to-mp323.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': "5e6976078bmsheb89f5f8d17f7d4p1b5895jsnb31e587ad8cc",
                'x-rapidapi-host': "youtube-to-mp323.p.rapidapi.com"
            }

            # Encode the YouTube URL
            request_url = f"/api.php?yt={url.replace('https://', '').replace('http://', '')}"
            conn.request("GET", request_url, headers=headers)

            # Get the response
            res = conn.getresponse()
            data = res.read()

            # Print the raw response for debugging
            print("Raw API Response:", data.decode("utf-8"))

            result = json.loads(data.decode("utf-8"))

            # Check if the API returned an error or unexpected result
            if result.get("status") != "ok":
                await interaction.followup.send(f"Failed to convert the video. Response: {result}", ephemeral=True)
                return

            # Get the download link from the response
            mp3_url = result.get("link")
            if not mp3_url:
                await interaction.followup.send("Could not retrieve the MP3 link. Please try again later.", ephemeral=True)
                return

            # Send the MP3 download link to the user
            await interaction.followup.send(f"Here is your MP3 file: [Download MP3]({mp3_url})", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(YouTubeMP3(bot))
