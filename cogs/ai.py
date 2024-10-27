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
            ai_response = result.get("contents", [{}])[0].get("parts", [{}])[0].get("text", "I couldn't find an answer.")
            await ctx.send(f"Spectra: {ai_response}")
        else:
            await ctx.send("Error: Unable to fetch a response from AI.")

async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
