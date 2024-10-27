import discord
from discord.ext import commands
import requests
import json

# Using your provided Google Gemini API key
API_KEY = 'AIzaSyB8kx3kPnaCJQtcXnZa-QnPS0uNgYIFwoM'

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ai", description="Start a conversation with Spectra using AI.")
    async def ai(self, ctx: commands.Context, *, prompt: str):
        # Notify the user that the bot is processing the request
        await ctx.send("Thinking...")

        # Define the request payload for the AI API
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        # Set up headers and URL, then send the request to Google Gemini API
        headers = {
            'Content-Type': 'application/json'
        }
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check if the response is successful
        if response.status_code == 200:
            result = response.json()
            # Output the raw JSON response for debugging
            print("API Response:", result)

            # Extract AI response or show a message if the content structure is unexpected
            try:
                ai_response = result["contents"][0]["parts"][0]["text"]
                await ctx.send(f"Spectra: {ai_response}")
            except (IndexError, KeyError):
                await ctx.send("Spectra: I couldn't find an answer in the expected format.")
        else:
            # Show the error message and status code for further investigation
            await ctx.send(f"Error: Unable to fetch a response from AI. Status code: {response.status_code}, Response: {response.text}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
