import discord
from discord.ext import commands
import requests
import json

# Replace 'YOUR_API_KEY' with your Google Gemini API key
API_KEY = 'AIzaSyB8kx3kPnaCJQtcXnZa-QnPS0uNgYIFwoM'

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ai", description="Start a conversation with Spectra using AI.")
    async def ai(self, ctx, prompt: str):
        # Send a message to indicate processing
        await ctx.respond("Thinking...")

        # Define the request payload
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

        # Set up the headers and send the request to Google Gemini
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

def setup(bot):
    bot.add_cog(AI(bot))
